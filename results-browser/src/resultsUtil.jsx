import Moment from "moment";

export const getPlainFiles = (resultData) => {
  if (resultData.length === 0) return { plainFiles: [], totalCount: 0 };

  // First directory is "." (the results dir)
  const resultsDirectories = resultData[0].contents;
  return {
    plainFiles: resultsDirectories.flatMap(dir => {
      if (!dir.contents) return [];

      // Flatmap files of each directory
      return dir.contents.map(file => ({
        key: file.name.substring((2)), // Cut "./" from the file name
        modified: +Moment(file.time),
        size: file.size,
      }));
    }),
    totalCount: resultsDirectories.length,
  };
};

export const getFileStatistics = (plainFiles) => {
  if (plainFiles.length === 0) return {};

  const getFileStatistic = (file) => {
    return plainFiles.filter(plainFile => plainFile.key.endsWith(file)).length;
  };

  return {
    "cpython-test.log": getFileStatistic("cpython-test.log"),
    "cpython-test-results.xml": getFileStatistic("cpython-test-results.xml"),
    "graalpy-test.log": getFileStatistic("graalpy-test.log"),
    "graalpy-test-results.xml": getFileStatistic("graalpy-test-results.xml"),
  };
};
