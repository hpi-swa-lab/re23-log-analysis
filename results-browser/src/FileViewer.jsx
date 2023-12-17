import React, { useEffect, useMemo } from "react";
import XMLViewer from "react-xml-viewer";
import { JsonView, defaultStyles } from "react-json-view-lite";
import "react-json-view-lite/dist/index.css";
import "./FileViewer.css";

const FileViewer = ({ file, searchString }) => {
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

  }, [file]);

  // Scroll to first appearance of search string in content (not regex compatible)
  useEffect(() => {
    if (!searchString) return;

    // https://stackoverflow.com/a/69711130
    const windowFind = () => {
      const wrapper = document.getElementsByClassName("fileContent")[0];
      if (window.find(searchString, true) ) {
        const s = window.getSelection();
        const oRange = s.getRangeAt(0);
        const oRect = oRange.getBoundingClientRect();
        const scrollTo =( oRect.top - wrapper.offsetTop)+wrapper.scrollTop;
        wrapper.scrollTo({ top: scrollTo });
      }
    }
    // Scroll to input field (ignore)
    windowFind();
    // Scroll to first appearance in actual content
    windowFind();
  }, [file, searchString]);

  return (
    <div className="file-viewer">
      { fileInfo }
      <div className="fileContent">
        { fileContentView }
      </div>
    </div>
  );
};

export default FileViewer;
