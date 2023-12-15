import React, { useMemo } from "react";
import XMLViewer from "react-xml-viewer";
import { JsonView, defaultStyles } from 'react-json-view-lite';
import 'react-json-view-lite/dist/index.css';
import "./FileViewer.css";

const FileViewer = ({ file }) => {
  const fileInfo = <b>{ file.key }</b>

  const fileContentView = useMemo(() => {
    const fileEnding = file.key.split(".").pop();
    switch (fileEnding) {
      case "json":
        return <JsonView data={ JSON.parse(file.content) } style={ defaultStyles } />
      case "xml":
        return <XMLViewer xml={ file.content } />
      case "log":
        return <div className="logView">{ file.content }</div>
      default:
        return null;
    }

  }, [file])

  return (
    <div className="fileViewer">
      { fileInfo }
      <div className="fileContent">
        { fileContentView }
      </div>
    </div>
  );
};

export default FileViewer;
