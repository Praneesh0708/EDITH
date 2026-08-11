import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [interviewStarted, setInterviewStarted] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [questionNumber, setQuestionNumber] = useState(0);

  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const [transcribedAnswer, setTranscribedAnswer] = useState("");

  // --------------------------------------------------------
  // Check Backend
  // --------------------------------------------------------

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/status")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(
          data.backend === "online"
            ? "Backend Connected"
            : "Backend Offline"
        );
      })
      .catch(() => {
        setBackendStatus("Backend Offline");
      });
  }, []);

  // --------------------------------------------------------
  // EDITH Text-to-Speech
  // --------------------------------------------------------

  const speakQuestion = (text) => {
    if (!text) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => {
      setSpeaking(true);
    };

    utterance.onend = () => {
      setSpeaking(false);
    };

    utterance.onerror = () => {
      setSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  // --------------------------------------------------------
  // Start Interview
  // --------------------------------------------------------

  const startInterview = async () => {
    try {
      setError("");

      // Camera + Microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      videoRef.current.srcObject = stream;

      // Start backend interview session
      const response = await fetch(
        "http://127.0.0.1:8000/interview/start",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to start interview");
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(
          data.message || "Interview could not be started"
        );
      }

      // Store session information
      setSessionId(data.session_id);
      setQuestion(data.question);
      setQuestionNumber(data.question_number);

      setInterviewStarted(true);

      // EDITH speaks first question
      speakQuestion(data.question);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Camera, microphone, or backend connection failed."
      );
    }
  };

  // --------------------------------------------------------
  // Start Voice Recording
  // --------------------------------------------------------

  const startRecording = () => {
    if (speaking) {
      return;
    }

    try {
      const stream = videoRef.current?.srcObject;

      if (!stream) {
        setError("Camera and microphone are not active.");
        return;
      }

      audioChunksRef.current = [];

      // Use only microphone audio
      const audioStream = new MediaStream(
        stream.getAudioTracks()
      );

      let recorder;

      if (
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus"
        )
      ) {
        recorder = new MediaRecorder(audioStream, {
          mimeType: "audio/webm;codecs=opus",
        });
      } else if (
        MediaRecorder.isTypeSupported("audio/webm")
      ) {
        recorder = new MediaRecorder(audioStream, {
          mimeType: "audio/webm",
        });
      } else {
        recorder = new MediaRecorder(audioStream);
      }

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: recorder.mimeType,
          }
        );

        console.log("Audio blob:", audioBlob);
        console.log("Audio size:", audioBlob.size);
        console.log("Audio type:", audioBlob.type);

        await sendVoiceAnswer(audioBlob);
      };

      recorder.start();

      setRecording(true);
      setError("");
      setTranscribedAnswer("");
    } catch (err) {
      console.error(err);
      setError("Unable to start voice recording.");
    }
  };

  // --------------------------------------------------------
  // Stop Voice Recording
  // --------------------------------------------------------

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  // --------------------------------------------------------
  // Send Voice Answer
  // --------------------------------------------------------

  const sendVoiceAnswer = async (audioBlob) => {
    try {
      setProcessing(true);
      setError("");

      const formData = new FormData();

      formData.append("session_id", sessionId);

      formData.append(
        "audio_file",
        audioBlob,
        "answer.webm"
      );

      const response = await fetch(
        "http://127.0.0.1:8000/interview/voice-answer",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        console.error(
          "Voice answer error:",
          errorText
        );

        throw new Error(
          `Voice answer failed: ${response.status}`
        );
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(
          data.message ||
            "Voice answer processing failed."
        );
      }

      // Display transcription
      setTranscribedAnswer(
        data.transcribed_answer || ""
      );

      // ----------------------------------------------------
      // Next Question
      // ----------------------------------------------------

      if (data.next_question) {
        const nextQuestion =
          data.next_question.question || "";

        setQuestion(nextQuestion);

        setQuestionNumber(
          (previous) => previous + 1
        );

        // EDITH speaks next question
        speakQuestion(nextQuestion);
      }
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  };

  // --------------------------------------------------------
  // UI
  // --------------------------------------------------------

  return (
    <div className="app">

      {/* -------------------------------------------------- */}
      {/* Header */}
      {/* -------------------------------------------------- */}

      <header className="header">

        <div>
          <h1>EDITH</h1>
          <p>AI Interview & Placement Coach</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>

          {interviewStarted
            ? "Interview Active"
            : backendStatus}
        </div>

      </header>

      {/* -------------------------------------------------- */}
      {/* Main */}
      {/* -------------------------------------------------- */}

      <main className="dashboard">

        {/* Welcome */}
        <section className="welcome">

          <h2>
            {interviewStarted
              ? "Your Interview Has Started"
              : "Welcome to EDITH"}
          </h2>

          <p>
            {interviewStarted
              ? "EDITH is ready to analyze your interview."
              : "Your adaptive AI-powered interview preparation assistant."}
          </p>

        </section>

        {/* ------------------------------------------------ */}
        {/* Preparation Cards */}
        {/* ------------------------------------------------ */}

        {!interviewStarted && (

          <section className="cards">

            <div className="card">

              <h3>📄 Resume</h3>

              <p>
                Upload your resume to create a
                personalized interview.
              </p>

              <button>
                Upload Resume
              </button>

            </div>

            <div className="card">

              <h3>💼 Job Role</h3>

              <p>
                Select the role you want to prepare for.
              </p>

              <select>

                <option>
                  Select Job Role
                </option>

                <option>
                  Software Developer
                </option>

                <option>
                  Python Developer
                </option>

                <option>
                  Java Developer
                </option>

                <option>
                  AI/ML Engineer
                </option>

                <option>
                  Data Scientist
                </option>

              </select>

            </div>

            <div className="card">

              <h3>🎯 Interview Type</h3>

              <p>
                Choose the type of interview
                you want to practice.
              </p>

              <select>

                <option>
                  Select Interview Type
                </option>

                <option>
                  Technical
                </option>

                <option>
                  HR
                </option>

                <option>
                  Technical + HR
                </option>

                <option>
                  AI/ML
                </option>

              </select>

            </div>

          </section>
        )}

        {/* ------------------------------------------------ */}
        {/* Camera + Interview */}
        {/* ------------------------------------------------ */}

        <section className="camera-section">

          {/* Camera */}
          <div className="camera-box">

            {!interviewStarted && (

              <>
                <div className="camera-icon">
                  📷
                </div>

                <h3>
                  Camera Preview
                </h3>

                <p>
                  Your camera will appear here
                  during the interview.
                </p>
              </>

            )}

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={
                interviewStarted
                  ? "camera-video"
                  : "hidden"
              }
            />

          </div>

          {/* Interview Panel */}
          <div className="interview-panel">

            <h2>

              {interviewStarted
                ? "Interview in Progress"
                : "Ready for your interview?"}

            </h2>

            {/* -------------------------------------------- */}
            {/* Active Interview */}
            {/* -------------------------------------------- */}

            {interviewStarted && (

              <>

                {/* Question */}
                <div className="question-box">

                  <div className="question-header">

                    <span>
                      Question {questionNumber}
                    </span>

                    {speaking && (

                      <span className="speaking-label">
                        🔊 EDITH speaking
                      </span>

                    )}

                  </div>

                  {/* Progress */}
                  <div className="question-progress">

                    <div
                      className="question-progress-bar"
                      style={{
                        width: `${Math.min(
                          questionNumber * 10,
                          100
                        )}%`,
                      }}
                    ></div>

                  </div>

                  <h3>
                    {question}
                  </h3>

                </div>

                {/* Session Information */}
                <div className="session-info">

                  <span>
                    🟢 Session Active
                  </span>

                  <span>
                    Session:{" "}
                    {sessionId
                      ? `${sessionId.slice(0, 8)}...`
                      : ""}
                  </span>

                </div>

                {/* Voice Status */}
                <div className="voice-status">

                  {speaking && (

                    <div className="recording-status">
                      🔊 EDITH is speaking...
                    </div>

                  )}

                  {recording && (

                    <div className="recording-status">
                      🔴 Listening to your answer...
                    </div>

                  )}

                  {processing && (

                    <div className="recording-status">
                      🧠 Analyzing your answer...
                    </div>

                  )}

                </div>

                {/* ---------------------------------------- */}
                {/* Voice Controls */}
                {/* ---------------------------------------- */}

                <div className="voice-controls">

                  {!recording &&
                    !processing &&
                    !speaking && (

                      <button
                        className="start-button"
                        onClick={startRecording}
                      >
                        🎤 Start Answer
                      </button>

                    )}

                  {recording && (

                    <button
                      className="start-button"
                      onClick={stopRecording}
                    >
                      ⏹ Stop Recording
                    </button>

                  )}

                </div>

                {/* ---------------------------------------- */}
                {/* Transcription */}
                {/* ---------------------------------------- */}

                {transcribedAnswer && (

                  <div className="answer-box">

                    <h3>
                      Your Answer
                    </h3>

                    <p>
                      {transcribedAnswer}
                    </p>

                  </div>

                )}

              </>

            )}

            {/* -------------------------------------------- */}
            {/* Before Interview */}
            {/* -------------------------------------------- */}

            {!interviewStarted && (

              <>

                <p>
                  EDITH will analyze your answers,
                  communication, technical knowledge
                  and identify areas for improvement.
                </p>

                <button
                  className="start-button"
                  onClick={startInterview}
                >
                  🎤 Start Interview
                </button>

              </>

            )}

            {/* Error */}
            {error && (

              <p className="error-message">
                {error}
              </p>

            )}

          </div>

        </section>

      </main>

      {/* -------------------------------------------------- */}
      {/* Footer */}
      {/* -------------------------------------------------- */}

      <footer>

        <p>
          EDITH • Adaptive AI Interview System
        </p>

      </footer>

    </div>
  );
}

export default App;