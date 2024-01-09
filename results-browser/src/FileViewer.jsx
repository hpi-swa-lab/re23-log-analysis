import React, { useEffect, useMemo, useState } from "react";
import XMLViewer from "react-xml-viewer";
import { JsonView, defaultStyles } from "react-json-view-lite";
import "react-json-view-lite/dist/index.css";
import SyntaxHighlighter from "react-syntax-highlighter";
import { vs } from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { Alert, CircularProgress } from "@mui/material";
import "./FileViewer.css";

const FileViewer = ({ file, searchString, furtherInspectionMessage, onLazyFileLoad }) => {
  const [lazyLoading, setLazyLoading] = useState(false);

  useEffect(() => {
    // If the user clicked the "graalpy-tmp.tar.gz entry,
    // we need to lazy load the included files.
    if (file.key.includes("graalpy-tmp.tar.gz")) {
      setLazyLoading(true);
      onLazyFileLoad(file).then(() => setLazyLoading(false));
    }
  }, [file, onLazyFileLoad]);

  const furtherInspectionInfo = useMemo(() => {
    if (!furtherInspectionMessage) return null;
    return (
      <Alert severity="info">
        { furtherInspectionMessage }
      </Alert>
    );
  }, [furtherInspectionMessage]);

  const fileContentView = useMemo(() => {
    if (!file.content) return;
    const fileEnding = file.key.split(".").pop();
    switch (fileEnding) {
      case "json":
        return <JsonView data={ JSON.parse(file.content) } style={ defaultStyles } />
      case "xml":
        return <XMLViewer xml={ file.content } />
      case "py":
        return (
          <SyntaxHighlighter language="python" style={ vs } showLineNumbers wrapLongLines>
            { file.content }
          </SyntaxHighlighter>
        );
      default:
        return <div className="log-view">{ file.content }</div>;
    }
  }, [file]);

  // Scroll to first appearance of search string in content (not regex compatible)
  useEffect(() => {
    const wrapperElements = document.getElementsByClassName("file-content");
    if (!wrapperElements[0]) {
      // There is no file's content displayed.
      return;
    }
    const wrapper = wrapperElements[0];
    if (!searchString) {
      // If no search string was given, just scroll back to the top.
      wrapper.scrollTo({ top: 0 });
      return;
    }

    // https://stackoverflow.com/a/69711130
    const windowFind = () => {
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

  if (lazyLoading) {
    return (
      <div className="file-viewer">
        <CircularProgress />
      </div>
    );
  }

  const fileInfo = <b>{ file.key }</b>
  const fileContentSection = (
    <>
      { fileInfo }
      <div className="file-content">
        { fileContentView }
      </div>
    </>
  );

  return (
    <div className="file-viewer">
      { furtherInspectionInfo }
      { file.content && fileContentSection }
    </div>
  );
};

export default FileViewer;
