import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import "./ResultsBrowser.css";
import { getFileStatistics, getPlainFiles } from "./resultsUtil";

const ResultsBrowser = () => {
  const [resultData, setResultData] = useState([]);

  useEffect(() => {
    fetch("results_index.json")
      .then(response => response.json())
      .then(data => setResultData(data))
      .catch(error => console.error(error.message))
  }, []);

  const { plainFiles, totalCount } = useMemo(() => getPlainFiles(resultData), [resultData]);
  const fileCounts = useMemo(() => getFileStatistics(plainFiles), [plainFiles]);

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
        canFilter
        showFoldersOnFilter
      />
    </div>
  );
}

export default ResultsBrowser;
