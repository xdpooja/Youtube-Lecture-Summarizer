import React, { useState } from "react";

const YouTubeForm = ({ onSummary }) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch("http://127.0.0.1:8000/converter/api/summarize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ video_url: videoUrl }),
      });

      if (!response.ok) {
        throw new Error("Something went wrong. Please check the URL or try again.");
      }

      const data = await response.json();
      if (data.summary) {
        onSummary(data.summary);
      } else {
        setError("No summary returned from the server.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="youtube-form-container p-4 bg-gray-100 rounded-2xl shadow-lg">
      <h2 className="text-xl font-bold mb-2">YouTube Video Summarizer</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          className="w-full p-2 border rounded-xl mb-2 focus:outline-none focus:ring-2 focus:ring-blue-300"
          placeholder="Enter YouTube Video URL"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl font-medium"
        >
          {loading ? "Summarizing..." : "Summarize"}
        </button>
      </form>

      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
};

export default YouTubeForm;
