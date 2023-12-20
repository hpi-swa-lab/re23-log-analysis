import Moment from "moment";

const _getFlattenedFiles = (contents) => {
  if (!contents) return [];
  // Recursively flatmap files of each directory
  return contents.flatMap(content => {
    if (content.type === "directory") {
      return _getFlattenedFiles(content.contents);
    }
    return [{
      key: content.name.substring((2)), // Cut the first "./" from the file name
      modified: +Moment(content.time),
      size: content.size,
    }];
  });
}

export const getFlattenedFiles = (resultData) => {
  if (resultData.length === 0) return [];
  // First directory is "." (the results dir)
  return _getFlattenedFiles(resultData[0].contents);
};

export const getFileStatistics = (flattenedFiles, includeCPython = true, includeGraalPy = true) => {
  if (flattenedFiles.length === 0) return {};

  // For counting files
  const getFileStatistic = (file) => {
    return flattenedFiles.filter(flattenedFile => flattenedFile.key.endsWith(file)).length;
  };

  // For counting packages
  const packages = flattenedFiles.map(flattenedFile => flattenedFile.key.split("/")[0]); // package identifier
  const uniquePackages = new Set(packages);

  const cpythonFiles = includeCPython ? {
    "cpython-install.log": getFileStatistic("cpython-install.log"),
    "cpython-test.log": getFileStatistic("cpython-test.log"),
    "cpython-test-results.xml": getFileStatistic("cpython-test-results.xml"),
  } : {};

  const graalPyFiles = includeGraalPy ? {
    "graalpy-install.log": getFileStatistic("graalpy-install.log"),
    "graalpy-test.log": getFileStatistic("graalpy-test.log"),
    "graalpy-test-results.xml": getFileStatistic("graalpy-test-results.xml"),
  } : {};

  return {
    "packages": uniquePackages.size,
    ...cpythonFiles,
    ...graalPyFiles,
  };
};
