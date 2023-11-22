import React, { useEffect, useMemo, useState } from "react";
import FileBrowser from "react-keyed-file-browser";
import "./ResultsBrowser.css";
import { getPlainFiles } from "./resultsUtil";

const ResultsBrowser = () => {
  const [resultData, setResultData] = useState([]);

  useEffect(() => {
    fetch("results_index.json")
      .then(response => response.json())
      .then(data => setResultData(data))
      .catch(error => console.error(error.message))
  }, []);

  const plainFiles = useMemo(() => getPlainFiles(resultData), [resultData]);

  return (
    <div className="results-browser">
      <FileBrowser
        files={ plainFiles }
        canFilter
        showFoldersOnFilter
      />
    </div>
  );
}

export default ResultsBrowser;
