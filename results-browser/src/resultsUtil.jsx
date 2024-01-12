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

const convertTarFilesToBrowserFormat = (tarFiles, pathOfTar) => {
  // Filter out directories (tar returns them separately)
  const plainFiles = tarFiles.filter(file => !file.name.endsWith("/") && !file.name.includes("@LongLink"));
  const textDecoder = new TextDecoder();
  return plainFiles.map(file => ({
    key: `${pathOfTar.split("/")[0]}/${file.name}`, // Prepend the directory the graalpy-tmp-tar was requested from to the file name
    modified: +Moment.unix(file.mtime),
    size: file.size,
    content: textDecoder.decode(file.buffer), // Get text content
  }));
};

export const getNewResultFilesAfterLazyLoad = (prevFiles, newTarFiles, pathOfTar) => {
  // Don't re-include the tar when we already unpacked its files.
  const prevFilesWithoutTarball = prevFiles.filter(prevFile => prevFile.key !== pathOfTar);
  const tarFilesInBrowserFormat = convertTarFilesToBrowserFormat(newTarFiles, pathOfTar);
  if (prevFiles.find(prevFile => prevFile.key === tarFilesInBrowserFormat[0].key)) {
    // Be idempotent
    return prevFilesWithoutTarball;
  } else {
    return [...prevFilesWithoutTarball, ...tarFilesInBrowserFormat];
  }
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

export const filterResultFiles = (filesWithContent, filterContentInput, filterNameInput, includeCPython = true, includeGraalPy = true) => {
  // First filter based on whether cpython/graalpy should be included
  let filesToInclude = filesWithContent;
  if (!includeCPython) {
    filesToInclude = filesToInclude.filter(file => !file.key.includes("cpython"));
  }
  if (!includeGraalPy) {
    filesToInclude = filesToInclude.filter(file => !file.key.includes("graalpy"));
  }
  if (!filterNameInput && !filterContentInput) return filesToInclude;

  // First: name based filtering
  let nameFilteredFiles = filesToInclude;
  if (filterNameInput) {
    try {
      const filterNameRegex = new RegExp(filterNameInput.toString());
      const nameRegexPredicate = file => file.key.match(filterNameRegex);
      nameFilteredFiles = nameFilteredFiles.filter(nameRegexPredicate);
    } catch (e) {
      // Regexp not parseable --> just try with includes as fallback
      const nameIncludesPredicate = file => file.key.includes(filterNameInput);
      nameFilteredFiles = nameFilteredFiles.filter(nameIncludesPredicate);
    }
  }

  if (!filterContentInput) return nameFilteredFiles;

  // Some files should not be further filtered by content afterward.
  const noContentFilterPattern = [
    // If GraalPy failed (partly or even completely), the scripts also dumps
    // tmp files created for the GraalPy run in the .tox directory.
    // But these files should not be filtered by the content in order to make
    // them available for inspection through the file browser.
    "graalpy-tmp",
  ];
  const noContentFilterPredicate = file => {
    for (const pattern of noContentFilterPattern) {
      if (file.key.includes(pattern)) return true;
    }
    return false;
  };

  // Second: content based filtering
  let contentFilteredFiles;
  try {
    const filterContentRegex = new RegExp(filterContentInput.toString());
    const contentRegexPredicate = file => file.content.match(filterContentRegex);
    contentFilteredFiles = nameFilteredFiles.filter(file => !noContentFilterPredicate(file) && contentRegexPredicate(file));
  } catch (e) {
    // Regexp not parseable --> just try with includes as fallback
    const contentIncludesPredicate = file => file.content.includes(filterContentInput);
    contentFilteredFiles = nameFilteredFiles.filter(file => !noContentFilterPredicate(file) && contentIncludesPredicate(file));
  }

  // For each package that got through the content filter, now re-include related files that were not be filtered by content.
  const results = contentFilteredFiles;
  const packages = new Set(contentFilteredFiles.map(file => file.key.split("/")[0]));
  packages.forEach(_package => {
    const notContentFilteredFilesForPackage = filesToInclude.filter(file => noContentFilterPredicate(file) && file.key.startsWith(_package));
    notContentFilteredFilesForPackage.forEach(file => results.push(file));
  });
  return results;
};

export const getFurtherInspectionMessage = (filteredFiles, selectedFile) => {
  // If for the package of the selected file there also is a "graalpy-tmp" directory that contains tmp test files,
  // we should display a message that graalpy error can be further inspected through the files in this directory.
  let message;
  const packageOfSelectedFile = selectedFile.key.split("/")[0];
  const selectedFileIsGraalPy = selectedFile.key.includes("graalpy");
  const graalPyTmpAvailable = filteredFiles.find(filteredFile => filteredFile.key.startsWith(`${packageOfSelectedFile}/graalpy-tmp`));
  if (selectedFileIsGraalPy && graalPyTmpAvailable) {
    message = `Further GraalPy error inspection possible - check out the "graalpy-tmp" directory for package ${packageOfSelectedFile}.`;
  }
  return message;
};
