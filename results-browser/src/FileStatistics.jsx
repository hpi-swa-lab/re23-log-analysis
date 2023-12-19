import React from "react";
import "./FileStatistics.css";

const FileStatistics = ({ fileStatistics }) =>
  <table className="file-statistics">
    <thead>
    <tr>
      <th>Subject</th>
      <th>Count</th>
    </tr>
    </thead>
    <tbody>
    {
      Object.entries(fileStatistics).map(([file, count]) => (
        <tr key={ file }>
          <td>{ file }</td>
          <td>{ count }</td>
        </tr>
      ))
    }
    </tbody>
  </table>;

export default FileStatistics;
