document.addEventListener("DOMContentLoaded", function () {
  const uploadBox = document.getElementById("upload-box");
  const fileInput = document.getElementById("files");
  const fileList = document.getElementById("file-list");
  const keywordSlider = document.getElementById("keyword_count");
  const keywordDisplay = document.getElementById("keyword-count-display");

  let selectedFiles = [];

  uploadBox.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    const newFiles = Array.from(fileInput.files);
    newFiles.forEach((file) => {
      if (
        !selectedFiles.find((f) => f.name === file.name && f.size === file.size)
      ) {
        selectedFiles.push(file);
      }
    });
    updateFileInput();
    renderFileList();
  });

  window.removeFile = function (index) {
    selectedFiles.splice(index, 1);
    updateFileInput();
    renderFileList();
  };

  function updateFileInput() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach((file) => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
  }

  function renderFileList() {
    fileList.innerHTML = "";
    selectedFiles.forEach((file, index) => {
      const item = document.createElement("div");
      item.className = "d-flex justify-content-between align-items-center mb-1";
      item.innerHTML = `
              <span>${file.name}</span>
              <button type="button" class="btn btn-sm btn-danger" onclick="removeFile(${index})">
                  <i class="fas fa-trash-alt"></i>
              </button>
          `;
      fileList.appendChild(item);
    });
  }

  keywordSlider.addEventListener("input", () => {
    keywordDisplay.textContent = keywordSlider.value;
  });
});
