import Moment from "moment";

export const getPlainFiles = (resultData) => {
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
    }))
  })
};
