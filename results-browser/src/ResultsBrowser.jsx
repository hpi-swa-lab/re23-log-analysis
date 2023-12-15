import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import "./ResultsBrowser.css";
import { getFileStatistics, getFlattenedFiles } from "./resultsUtil";
import FileViewer from "./FileViewer";

const ResultsBrowser = () => {
  const [loading, setLoading] = useState(true);
  const [resultsIndexData, setResultsIndexData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(undefined);
  const [filesWithContent, setFilesWithContent] = useState([]);
  const [filterRegexInput, setFilterRegexInput] = useState(undefined);

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

    Promise.all(
      flattenedFiles.map(async file => {
        console.log(`Loading ${file.key}`);
        const response = await fetch(`results/${file.key}`)
        const textContent = await response.text();
        return { ...file, content: textContent };
      })
    ).then(resultFiles => {
      setLoading(false);
      setFilesWithContent(resultFiles);
    });
  }, [flattenedFiles]);

  // Filter files
  const filteredFiles = useMemo(() => {
    if (!filterRegexInput) return filesWithContent;
    try {
      const filterRegex = new RegExp(filterRegexInput.toString());
      const regexPredicate = filesWithContent => filesWithContent.content.match(filterRegex);
      return filesWithContent.filter(regexPredicate);
    } catch (e) {
      // Regexp not parseable --> just try with includes as fallback
      const includesPredicate = filesWithContent => filesWithContent.content.includes(filterRegexInput);
      return filesWithContent.filter(includesPredicate);
    }
  }, [filesWithContent, filterRegexInput]);

  const filterFiles = (event) => {
    setSelectedFile(undefined);
    setFilterRegexInput(event.target.value);
  };

  const fileCounts = useMemo(() => getFileStatistics(filteredFiles), [filteredFiles]);

  const selectNewFile = (file) => {
    const fileWithContent = filesWithContent.find(fileWithContent => fileWithContent.key === file.key);
    setSelectedFile(fileWithContent);
  };

  if (loading) return "Loading files...";

  return (
    <div className="results-browser">
      <table className="results-statistics">
        <thead>
          <tr><th>Subject</th><th>Count</th></tr>
        </thead>
        <tbody>
          {
            Object.entries(fileCounts).map(([file, count]) => (
              <tr key={ file }><td>{ file }</td><td>{ count }</td></tr>
            ))
          }
        </tbody>
      </table>
      <div className="fileBrowserWithFilter">
        <input
          type="text"
          placeholder="Filter files based on Regex"
          onChange={ filterFiles }
        />
        <FileBrowser
          files={ filteredFiles }
          onSelectFile={ selectNewFile }
          canFilter={ false } // disable file browsers own filters
          noFilesMessage="No files available or matching"
          detailRenderer={ () => null }
        />
      </div>
      { selectedFile && filesWithContent && <FileViewer file={ selectedFile } searchString={ filterRegexInput } /> }
    </div>
  );
}

export default ResultsBrowser;