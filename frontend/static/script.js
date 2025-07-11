function uploadDoc() {
  const files = document.getElementById("file").files;
  const formData = new FormData();

  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  fetch("http://localhost:8000/upload", {
    method: "POST",
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      alert(data.msg);
      loadDocuments();
    })
    .catch(error => console.error("Upload error:", error));
}


function ask() {
  const q = document.getElementById("question").value;
  const formData = new FormData();
  formData.append("question", q);

  const responseBox = document.getElementById("response");
  const loading = document.getElementById("loading");

  responseBox.textContent = "";
  loading.classList.remove("hidden");

  fetch("http://localhost:8000/query", {
    method: "POST",
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      loading.classList.add("hidden");
      typeResponse(data.answer, responseBox);
    })
    .catch(error => {
      loading.classList.add("hidden");
      console.error("Query error:", error);
    });
}

// Typing animation for bot response
function typeResponse(text, element) {
  let index = 0;
  element.textContent = "";
  const interval = setInterval(() => {
    if (index < text.length) {
      element.textContent += text.charAt(index);
      index++;
    } else {
      clearInterval(interval);
    }
  }, 30);
}

//  Dark mode toggle
document.getElementById("toggleTheme").addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const btn = document.getElementById("toggleTheme");
  btn.textContent = document.body.classList.contains("dark")
    ? "☀️ Light Mode"
    : "🌙 Dark Mode";
});

//  Voice input
function startVoice() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.start();
  recognition.onresult = function(event) {
    const voiceText = event.results[0][0].transcript;
    document.getElementById("question").value = voiceText;
  };

  recognition.onerror = function(event) {
    alert("Voice input error: " + event.error);
  };
}


//  Load uploaded documents and show them with delete buttons
function loadDocuments() {
  fetch("http://localhost:8000/documents")
    .then(response => response.json())
    .then(data => {
      const list = document.getElementById("docList");
      const msg = document.getElementById("noDocsMsg");
      const askBtn = document.getElementById("askBtn");

      list.innerHTML = "";
      msg.textContent = "";

      if (data.documents.length === 0) {
        msg.textContent = "⚠️ No documents uploaded. Please upload to ask questions.";
        askBtn.disabled = true;
      } else {
        data.documents.forEach(doc => {
          const item = document.createElement("li");
          item.textContent = doc;

          const delBtn = document.createElement("button");
          delBtn.textContent = "  Delete";
          delBtn.onclick = () => deleteDocument(doc);

          item.appendChild(delBtn);
          list.appendChild(item);
        });
        askBtn.disabled = false;
      }
    });
}


function deleteDocument(filename) {
  fetch(`http://localhost:8000/documents/${filename}`, {
    method: "DELETE"
  })
    .then(response => response.json())
    .then(data => {
      alert(data.msg);
      loadDocuments(); // Refresh list
    });
}



//  Toggle document list visibility
function toggleDocList() {
  const docList = document.getElementById("docList");
  const toggleButton = document.getElementById("toggleDocListBtn");

  if (docList.style.display === "block") {
    docList.style.display = "none";
    toggleButton.textContent = " Show Documents";
  } else {
    docList.style.display = "block";
    toggleButton.textContent = " Hide Documents";
    loadDocuments();
  }
}
