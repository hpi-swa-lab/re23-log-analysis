import untar from "js-untar";
import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import { FolderOpen, FolderOutlined, InsertDriveFileOutlined } from "@mui/icons-material";
import { Alert, LinearProgress } from "@mui/material";
import "./ResultsBrowser.css";
import { filterResultFiles, getFileStatistics, getFurtherInspectionMessage, getFlattenedFiles, getNewResultFilesAfterLazyLoad } from "./resultsUtil";
import FileViewer from "./FileViewer";
import FileStatistics from "./FileStatistics";

const ResultsBrowser = () => {
  const [loadingProgress, setLoadingProgress] = useState({ progress: 0 });
  const [resultsIndexData, setResultsIndexData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(undefined);
  const [filesWithContent, setFilesWithContent] = useState([]);
  const [filterContentInput, setFilterContentInput] = useState(undefined);
  const [filterNameInput, setFilterNameInput] = useState(undefined);
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

  // Enrich basic result files with their contents
  useEffect(() => {
    if (flattenedFiles.length === 0) return [];

    const getFilesWithContents = async () => {
      const results = [];
      for (const [index, file] of flattenedFiles.entries()) {
        if (file.key.includes("graalpy-tmp.tar.gz")) {
          // But skip content fetching for the "graalpy-tmp" directory,
          // as we lazy load its content only if necessary.
          results.push(file);
          continue;
        }
        const response = await fetch(`results/${file.key}`);
        const textContent = await response.text();
        results.push({ ...file, content: textContent });
        setLoadingProgress({
          progress: (index + 1) / flattenedFiles.length * 100,
          directory: file.key.split("/")[0],
        });
      }
      return results;
    };

    getFilesWithContents()
      .then(resultFiles => {
        setLoadingProgress(undefined);
        setFilesWithContent(resultFiles);
      })
      .catch(error => setLoadingProgress(prevState => ({
        ...prevState,
        error: error.message,
      })));
  }, [flattenedFiles]);

  const handleLazyFileLoad = async (fileToLazyLoad) => {
    if (!fileToLazyLoad.key.includes("graalpy-tmp.tar.gz")) {
      // lazy loading and extraction only for graalpy-tmp directory expected
      return;
    }
    fetch(`results/${fileToLazyLoad.key}`)
      .then(response => response.blob())
      // Decompress the tar archive
      .then(blob => {
        const ds = new DecompressionStream("gzip");
        const decompressedStream = blob.stream().pipeThrough(ds);
        return new Response(decompressedStream).blob();
      })
      .then(blob => blob.arrayBuffer())
      // Extract files from graalpy-tmp tarball using js-untar
      .then(decompressed => {
        untar(decompressed)
          .then(
            tarFiles => setFilesWithContent(prevFiles => getNewResultFilesAfterLazyLoad(prevFiles, tarFiles, fileToLazyLoad.key)),
            error => console.error(error)
          )
      })
      .catch(error => console.error(error));
  };

  // Filter files
  const filteredFiles = useMemo(
    () => filterResultFiles(filesWithContent, filterContentInput, filterNameInput, includeCPython, includeGraalPy)
  , [filesWithContent, filterContentInput, filterNameInput, includeCPython, includeGraalPy]);

  // Get file statistics
  const fileStatistics = useMemo(
    () => getFileStatistics(filteredFiles, includeCPython, includeGraalPy)
    , [filteredFiles, includeCPython, includeGraalPy]);

  const handleContentFilterChange = (event) => {
    setSelectedFile(undefined);
    setFilterContentInput(event.target.value);
  };

  const handleNameFilterChange = (event) => {
    setSelectedFile(undefined);
    setFilterNameInput(event.target.value);
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

  if (loadingProgress) {
    const { directory, error, progress } = loadingProgress;
    return (
      <div className="loading">
        <div className="loading-indicator">
          <div>
            <LinearProgress variant="determinate" value={ progress } />
          </div>
          { Math.round(progress) }%
        </div>
        { directory && <div>Loading files for { directory }</div> }
        { error && <Alert severity="error">{ error }</Alert> }
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
            placeholder="Filter file name"
            onChange={ handleNameFilterChange }
          />
          <input
            type="text"
            placeholder="Filter file content"
            onChange={ handleContentFilterChange }
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
            searchString={ filterContentInput }
            furtherInspectionMessage={ getFurtherInspectionMessage(filteredFiles, selectedFile) }
            onLazyFileLoad={ handleLazyFileLoad }
          />
      }
    </div>
  );
}

export default ResultsBrowser;
