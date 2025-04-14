// scripts.js
document.addEventListener("DOMContentLoaded", function () {
  // File upload functionality
  const uploadBox = document.getElementById("upload-box");
  const fileInput = document.getElementById("files");
  const fileList = document.getElementById("file-list");

  // We'll use a regular array to store files since DataTransfer can be tricky
  let selectedFilesArray = [];

  if (uploadBox && fileInput) {
    uploadBox.addEventListener("click", function () {
      fileInput.click();
    });

    uploadBox.addEventListener("dragover", function (e) {
      e.preventDefault();
      uploadBox.classList.add("drag-over");
    });

    uploadBox.addEventListener("dragleave", function () {
      uploadBox.classList.remove("drag-over");
    });

    uploadBox.addEventListener("drop", function (e) {
      e.preventDefault();
      uploadBox.classList.remove("drag-over");

      if (e.dataTransfer.files.length) {
        addFiles(e.dataTransfer.files);
      }
    });

    fileInput.addEventListener("change", function () {
      if (fileInput.files.length) {
        addFiles(fileInput.files);
      }
      // Reset file input
      fileInput.value = "";
    });
  }

  // Function to add files to our collection
  function addFiles(newFiles) {
    for (let i = 0; i < newFiles.length; i++) {
      selectedFilesArray.push(newFiles[i]);
    }
    updateFileList();
    updateFileInput();
  }

  // Update the file input with our array of files
  function updateFileInput() {
    // Create a new DataTransfer object
    const dataTransfer = new DataTransfer();

    // Add all files from our array
    selectedFilesArray.forEach((file) => {
      dataTransfer.items.add(file);
    });

    // Set the files property of the file input
    fileInput.files = dataTransfer.files;
  }

  // Function to update file list display
  function updateFileList() {
    if (!fileList) return;

    fileList.innerHTML = "";

    if (selectedFilesArray.length > 0) {
      selectedFilesArray.forEach((file, index) => {
        const fileItem = document.createElement("div");
        fileItem.className = "file-item";

        const fileIcon = document.createElement("i");
        fileIcon.className = file.name.endsWith(".pdf")
          ? "fas fa-file-pdf"
          : "fas fa-file-word";

        const fileName = document.createElement("span");
        fileName.className = "file-item-name";
        fileName.textContent = file.name;

        const removeBtn = document.createElement("span");
        removeBtn.className = "file-item-remove";
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          removeFile(index);
        });

        fileItem.appendChild(fileIcon);
        fileItem.appendChild(fileName);
        fileItem.appendChild(removeBtn);

        fileList.appendChild(fileItem);
      });
    }
  }

  // Function to remove a file by index
  function removeFile(index) {
    // Remove the file at the specified index
    selectedFilesArray.splice(index, 1);

    // Update the UI and file input
    updateFileList();
    updateFileInput();
  }

  // Keyword count range input
  const keywordCountInput = document.getElementById("keyword_count");
  const keywordCountDisplay = document.getElementById("keyword-count-display");

  if (keywordCountInput && keywordCountDisplay) {
    keywordCountInput.addEventListener("input", function () {
      keywordCountDisplay.textContent = this.value;
    });
  }

  // Form validation
  const keywordForm = document.getElementById("keywordForm");

  if (keywordForm) {
    keywordForm.addEventListener("submit", function (e) {
      const textInput = document.getElementById("text").value;

      if (textInput.trim() === "" && selectedFilesArray.length === 0) {
        e.preventDefault();
        showError(
          "Please enter text or upload at least one file before submitting."
        );
      }
    });
  }

  // Error message display
  function showError(message) {
    // Check if error alert already exists
    const existingAlert = document.querySelector(".alert-danger");
    if (existingAlert) {
      existingAlert.remove();
    }

    const alertDiv = document.createElement("div");
    alertDiv.className = "alert alert-danger mt-3";
    alertDiv.role = "alert";
    alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

    const formElement = document.getElementById("keywordForm");
    formElement.insertBefore(alertDiv, formElement.firstChild);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
      alertDiv.classList.add("fade");
      setTimeout(() => alertDiv.remove(), 500);
    }, 5000);
  }

  // Animation effects
  const animateElements = document.querySelectorAll(
    ".intro-card, .content-card"
  );
  animateElements.forEach((element) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";
    element.style.transition = "opacity 0.5s ease, transform 0.5s ease";

    setTimeout(() => {
      element.style.opacity = "1";
      element.style.transform = "translateY(0)";
    }, 100);
  });
});
