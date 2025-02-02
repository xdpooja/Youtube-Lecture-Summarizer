import React, { useState } from "react";
import YouTubeForm from "./components/YoutubeForm";

function App() {
  const [summary, setSummary] = useState("");

  return (
    <div className="app-container p-6">
      <YouTubeForm onSummary={setSummary} />
      {summary && (
        <div className="summary-box mt-4 p-4 bg-gray-50 border rounded-xl shadow-md">
          <h2 className="text-lg font-semibold mb-2">Summary:</h2>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;
