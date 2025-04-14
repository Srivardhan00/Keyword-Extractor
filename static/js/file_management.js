document.addEventListener("DOMContentLoaded", function () {
  // Global variables
  let currentPage = 1;
  let limit = 10;
  let totalFiles = 0;
  let currentFileId = null;
  let fileKeywords = [];

  // DOM Elements
  const filesList = document.getElementById("filesList");
  const emptyState = document.getElementById("emptyState");
  const prevPage = document.getElementById("prevPage");
  const nextPage = document.getElementById("nextPage");
  const pageIndicator = document.getElementById("pageIndicator");

  // Bootstrap components
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const deleteModal = new bootstrap.Modal(
    document.getElementById("deleteModal")
  );
  const toast = new bootstrap.Toast(document.getElementById("toast"));

  // Form elements
  const editFileForm = document.getElementById("editFileForm");
  const editFileId = document.getElementById("editFileId");
  const editDescription = document.getElementById("editDescription");
  const keywordInput = document.getElementById("keywordInput");
  const keywordsList = document.getElementById("keywordsList");
  const saveFileChanges = document.getElementById("saveFileChanges");
  const confirmDelete = document.getElementById("confirmDelete");

  // Initialize the page
  loadFiles(currentPage);

  // Event listeners
  prevPage.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      loadFiles(currentPage);
    }
  });

  nextPage.addEventListener("click", () => {
    currentPage++;
    loadFiles(currentPage);
  });

  keywordInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      addKeyword(this.value);
      this.value = "";
    }
  });

  saveFileChanges.addEventListener("click", updateFile);
  confirmDelete.addEventListener("click", deleteFile);

  // Functions
  async function loadFiles(page) {
    filesList.innerHTML = `
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading files...</p>
    </div>
    `;

    try {
      let url = `/files?page=${page}&limit=${limit}`;


      console.log(`Fetching data from URL: ${url}`); // Debugging fetch URL

      const response = await fetch(url);
      const data = await response.json();

      console.log("Response data:", data); // Debugging response

      if (!response.ok) {
        throw new Error(data.error || "Failed to load files");
      }

      renderFiles(data);

      // Update pagination
      const hasMoreFiles = data.length === limit;
      updatePagination(page, hasMoreFiles);

      // Show empty state if needed
      if (data.length === 0) {
        filesList.innerHTML = "";
        emptyState.style.display = "block";
      } else {
        emptyState.style.display = "none";
      }
    } catch (error) {
      console.error("Error loading files:", error.message); // Debugging error
      showToast("Error", error.message, "error");
      filesList.innerHTML = `
        <div class="text-center p-4 text-danger">
        <i class="fas fa-exclamation-triangle"></i>
        <p>Failed to load files. Please try again.</p>
        </div>
    `;
    }
  }

  function renderFiles(files) {
    if (!files || files.length === 0) {
      return;
    }

    let html = "";

    files.forEach((file, index) => {
      // Get file extension icon
      const fileIcon = getFileTypeIcon(file.file_type);

      // Create keywords HTML
      const keywordsHtml = file.keywords
        .map((keyword) => `<span class="keyword">${keyword}</span>`)
        .join(" ");

      html += `
        <div class="file-item" style="animation-delay: ${index * 0.05}s;">
        <div class="file-name">${file.file_name}</div>
        <div class="file-description">${
          file.description || "No description"
        }</div>
        <div class="file-keywords">
            ${keywordsHtml || '<span class="keyword">No keywords</span>'}
        </div>
        <div class="file-type">${file.file_type.toUpperCase()}</div>
        <div class="file-actions">
            <button class="file-action-btn edit-btn" data-file-id="${file._id}">
            <i class="fas fa-edit"></i> edit
            </button>
            <button class="file-action-btn delete-btn" data-file-id="${
              file._id
            }" data-file-name="${file.file_name}">
            <i class="fas fa-trash"></i> del
            </button>
        </div>
        </div>
    `;
    });

    filesList.innerHTML = html;

    // Add event listeners to buttons
    document.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", () => openEditModal(btn.dataset.fileId));
    });

    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () =>
        openDeleteModal(btn.dataset.fileId, btn.dataset.fileName)
      );
    });
  }

  function updatePagination(page, hasMoreFiles) {
    pageIndicator.textContent = `Page ${page}`;
    prevPage.disabled = page <= 1;
    nextPage.disabled = !hasMoreFiles;
  }

  async function openEditModal(fileId) {
    try {
      const response = await fetch(`/files/${fileId}`);
      const file = await response.json();

      if (!response.ok) {
        throw new Error(file.error || "Failed to load file details");
      }

      // Set form values
      editFileId.value = file._id;
      editDescription.value = file.description || "";

      // Clear existing keywords
      keywordsList.innerHTML = "";
      fileKeywords = [...file.keywords];

      // Add keywords to the list
      fileKeywords.forEach((keyword) => {
        const keywordEl = createKeywordElement(keyword);
        keywordsList.appendChild(keywordEl);
      });

      // Show modal
      editModal.show();
    } catch (error) {
      console.error("Error opening edit modal:", error.message); // Debugging error
      showToast("Error", error.message, "error");
    }
  }

  function openDeleteModal(fileId, fileName) {
    currentFileId = fileId;
    document.getElementById("deleteFileName").textContent = fileName;
    deleteModal.show();
  }

  async function updateFile() {
    try {
      const fileId = editFileId.value;
      const description = editDescription.value;

      const response = await fetch(`/files/${fileId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description,
          keywords: fileKeywords,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to update file");
      }

      editModal.hide();
      showToast("Success", "File updated successfully", "success");
      loadFiles(currentPage);
    } catch (error) {
      console.error("Error updating file:", error.message); // Debugging error
      showToast("Error", error.message, "error");
    }
  }

  async function deleteFile() {
    try {
      const response = await fetch(`/files/${currentFileId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to delete file");
      }

      deleteModal.hide();
      showToast("Success", "File deleted successfully", "success");
      loadFiles(currentPage);
    } catch (error) {
      console.error("Error deleting file:", error.message); // Debugging error
      showToast("Error", error.message, "error");
    }
  }

  function addKeyword(keyword) {
    keyword = keyword.trim();

    if (!keyword || fileKeywords.includes(keyword)) {
      return;
    }

    fileKeywords.push(keyword);
    const keywordEl = createKeywordElement(keyword);
    keywordsList.appendChild(keywordEl);
  }

  function createKeywordElement(keyword) {
    const div = document.createElement("div");
    div.className = "keyword-item";
    div.innerHTML = ` 
    ${keyword}
    <button type="button" class="keyword-remove">
        <i class="fas fa-times"></i>
    </button>
    `;

    const removeBtn = div.querySelector(".keyword-remove");
    removeBtn.addEventListener("click", () => {
      div.remove();
      fileKeywords = fileKeywords.filter((k) => k !== keyword);
    });

    return div;
  }

  function getFileTypeIcon(fileType) {
    const icons = {
      pdf: "file-pdf",
      doc: "file-word",
      docx: "file-word",
      xls: "file-excel",
      xlsx: "file-excel",
      ppt: "file-powerpoint",
      pptx: "file-powerpoint",
      txt: "file-alt",
      csv: "file-csv",
      zip: "file-archive",
      rar: "file-archive",
      jpg: "file-image",
      jpeg: "file-image",
      png: "file-image",
      mp3: "file-audio",
      mp4: "file-video",
    };

    const type = fileType.toLowerCase();
    const iconName = icons[type] || "file";

    return `fa-${iconName}`;
  }

  function showToast(title, message, type = "info") {
    const toastTitle = document.getElementById("toastTitle");
    const toastMessage = document.getElementById("toastMessage");
    const toastElement = document.getElementById("toast");

    // Set toast content
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Set toast type
    toastElement.classList.remove(
      "bg-success",
      "bg-danger",
      "bg-info",
      "bg-warning"
    );

    switch (type) {
      case "success":
        toastElement.classList.add("bg-success");
        break;
      case "error":
        toastElement.classList.add("bg-danger");
        break;
      case "warning":
        toastElement.classList.add("bg-warning");
        break;
      default:
        toastElement.classList.add("bg-info");
    }

    // Show toast
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
  }

  // Debounce function for search input
  function debounce(func, delay) {
    let timeout;
    return function () {
      clearTimeout(timeout);
      timeout = setTimeout(func, delay);
    };
  }
});
