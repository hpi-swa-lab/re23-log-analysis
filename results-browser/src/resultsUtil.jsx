import Moment from "moment";

export const getFlattenedFiles = (resultData) => {
  if (resultData.length === 0) return [];

  // First directory is "." (the results dir)
  const resultsDirectories = resultData[0].contents;
  return resultsDirectories.flatMap(dir => {
    if (!dir.contents) return [];

    // Flatmap files of each directory
    return dir.contents.map(file => ({
      key: file.name.substring((2)), // Cut "./" from the file name
      modified: +Moment(file.time),
      size: file.size,
    }));
  });
};

export const getFileStatistics = (flattenedFiles) => {
  if (flattenedFiles.length === 0) return {};

  // For counting files
  const getFileStatistic = (file) => {
    return flattenedFiles.filter(flattenedFile => flattenedFile.key.endsWith(file)).length;
  };

  // For counting packages
  const packages = flattenedFiles.map(flattenedFile => flattenedFile.key.split("/")[0]); // package identifier
  const uniquePackages = new Set(packages);

  return {
    "packages": uniquePackages.size,
    "cpython-install.log": getFileStatistic("cpython-install.log"),
    "cpython-test.log": getFileStatistic("cpython-test.log"),
    "cpython-test-results.xml": getFileStatistic("cpython-test-results.xml"),
    "graalpy-install.log": getFileStatistic("graalpy-install.log"),
    "graalpy-test.log": getFileStatistic("graalpy-test.log"),
    "graalpy-test-results.xml": getFileStatistic("graalpy-test-results.xml"),
  };
};
