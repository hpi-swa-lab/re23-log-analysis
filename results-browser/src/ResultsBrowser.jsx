import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import "./ResultsBrowser.css";
import { getFileStatistics, getPlainFiles } from "./resultsUtil";
import FileViewer from "./FileViewer";

const ResultsBrowser = () => {
  const [resultsIndexData, setResultsIndexData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(undefined);
  const [selectedFileContent, setSelectedFileContent] = useState(undefined);

  useEffect(() => {
    fetch("results/results_index.json")
      .then(response => response.json())
      .then(data => setResultsIndexData(data))
      .catch(error => console.error(error.message))
  }, []);

  useEffect( () => {
    if (!selectedFile) return;
    fetch(`results/${selectedFile.key}`)
      .then(response => response.text())
      .then(data => {
        setSelectedFileContent(data);
      })
      .catch(error => console.error(error.message));
  }, [selectedFile]);

  const { plainFiles, totalCount } = useMemo(() => getPlainFiles(resultsIndexData), [resultsIndexData]);
  const fileCounts = useMemo(() => getFileStatistics(plainFiles), [plainFiles]);

  const selectNewFile = (file) => {
    setSelectedFileContent(undefined);
    setSelectedFile(file);
  };

  return (
    <div className="results-browser">
      <table className="results-statistics">
        <thead>
          <tr><th>Subject</th><th>Count</th></tr>
        </thead>
        <tbody>
          <tr><td>packages</td><td>{ totalCount }</td></tr>
          {
            Object.entries(fileCounts).map(([file, count]) => (
              <tr key={ file }><td>{ file }</td><td>{ count }</td></tr>
            ))
          }
        </tbody>
      </table>
      <FileBrowser
        files={ plainFiles }
        onSelectFile={ selectNewFile }
        canFilter
        showFoldersOnFilter
        detailRenderer={ () => null }
      />
      { selectedFile && selectedFileContent && <FileViewer file={ { ...selectedFile, content: selectedFileContent } } /> }
    </div>
  );
}

export default ResultsBrowser;
