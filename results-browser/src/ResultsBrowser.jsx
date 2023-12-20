import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import { FolderOpen, FolderOutlined, InsertDriveFileOutlined } from "@mui/icons-material";
import { LinearProgress } from "@mui/material";
import "./ResultsBrowser.css";
import { filterResultFiles, getFileStatistics, getFlattenedFiles, getFurtherInspectionMessage } from "./resultsUtil";
import FileViewer from "./FileViewer";
import FileStatistics from "./FileStatistics";

const ResultsBrowser = () => {
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [resultsIndexData, setResultsIndexData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(undefined);
  const [filesWithContent, setFilesWithContent] = useState([]);
  const [filterRegexInput, setFilterRegexInput] = useState(undefined);
  const [includeCPython, setIncludeCPython] = useState(true);
  const [includeGraalPy, setIncludeGraalPy] = useState(true);

  useEffect(() => {
    // Load index of result files
    fetch("results/results_index.json")
      .then(response => response.json())
      .then(data => setResultsIndexData(data))
      .catch(error => console.error(error.message))
  }, []);

  // Flat down directory structure
  const flattenedFiles = useMemo(() => getFlattenedFiles(resultsIndexData), [resultsIndexData]);

  // Enrich all result files with their contents
  useEffect(() => {
    if (flattenedFiles.length === 0) return [];

    const getFilesWithContents = async () => {
      const results = [];
      for (const [index, file] of flattenedFiles.entries()) {
        const response = await fetch(`results/${file.key}`);
        const textContent = await response.text();
        results.push({ ...file, content: textContent });
        setLoadingProgress((index + 1) / flattenedFiles.length * 100);
      }
      return results;
    };

    getFilesWithContents().then(resultFiles => {
      setLoadingProgress(undefined);
      setFilesWithContent(resultFiles);
    }).catch(error => console.error(error));
  }, [flattenedFiles]);

  // Filter files
  const filteredFiles = useMemo(
    () => filterResultFiles(filesWithContent, filterRegexInput, includeCPython, includeGraalPy)
  , [filesWithContent, filterRegexInput, includeCPython, includeGraalPy]);

  // Get file statistics
  const fileStatistics = useMemo(
    () => getFileStatistics(filteredFiles, includeCPython, includeGraalPy)
    , [filteredFiles, includeCPython, includeGraalPy]);

  const handleFilterFiles = (event) => {
    setSelectedFile(undefined);
    setFilterRegexInput(event.target.value);
  };

  const handleToggleIncludeCPython = (_) => {
    setSelectedFile(undefined);
    setIncludeCPython((prevState) => !prevState);
  };

  const handleToggleIncludeGraalPy = (_) => {
    setSelectedFile(undefined);
    setIncludeGraalPy((prevState) => !prevState);
  };

  const handleSelectNewFile = (file) => {
    const fileWithContent = filesWithContent.find(fileWithContent => fileWithContent.key === file.key);
    setSelectedFile(fileWithContent);
  };

  if (loadingProgress !== undefined) {
    return (
      <div className="loading">
        <div>
          <LinearProgress variant="determinate" value={ loadingProgress } />
        </div>
        { Math.round(loadingProgress) }%
      </div>
    );
  }

  return (
    <div className="results-browser">
      <FileStatistics fileStatistics={ fileStatistics } />
      <div className="file-browser-with-filter">
        <div className="filters">
          <input
            type="text"
            placeholder="Filter files based on Regex"
            onChange={ handleFilterFiles }
          />
          <input
            type="checkbox"
            name="includeCPython"
            checked={ includeCPython }
            onChange={ handleToggleIncludeCPython }
          />
          <label htmlFor="includeCPython">Show CPython files</label>
          <input
            type="checkbox"
            name="includeGraalPy"
            checked={ includeGraalPy }
            onChange={ handleToggleIncludeGraalPy }
          />
          <label htmlFor="includeGraalPy">Show GraalPy files</label>
        </div>
        <FileBrowser
          files={ filteredFiles }
          onSelectFile={ handleSelectNewFile }
          canFilter={ false } // disable file browsers own filters
          showActionBar={ false }
          noFilesMessage="No files available or matching"
          detailRenderer={ () => null }
          icons={{
            File: <InsertDriveFileOutlined />,
            Folder: <FolderOutlined />,
            FolderOpen: <FolderOpen />,
          }}
        />
      </div>
      {
        selectedFile && filteredFiles &&
          <FileViewer
            file={ selectedFile }
            searchString={ filterRegexInput }
            furtherInspectionMessage={ getFurtherInspectionMessage(filteredFiles, selectedFile) }
          />
      }
    </div>
  );
}

export default ResultsBrowser;
