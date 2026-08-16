
import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewEnded, setInterviewEnded] = useState(false);

  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] =
    useState("Checking...");

  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [questionNumber, setQuestionNumber] =
    useState(0);

  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const [transcribedAnswer, setTranscribedAnswer] =
    useState("");

  const [report, setReport] = useState(null);

  const [showEndConfirmation, setShowEndConfirmation] =
    useState(false);

  // =========================================================
  // CHECK BACKEND
  // =========================================================

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

  // =========================================================
  // TEXT TO SPEECH
  // =========================================================

  const speakQuestion = (text) => {
    if (!text) return;

    window.speechSynthesis.cancel();

    const utterance =
      new SpeechSynthesisUtterance(text);

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

  // =========================================================
  // START INTERVIEW
  // =========================================================

  const startInterview = async () => {
    try {
      setError("");

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

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
        throw new Error(
          "Failed to start interview"
        );
      }

      const data = await response.json();

      console.log(
        "START INTERVIEW RESPONSE:",
        data
      );

      if (data.status !== "success") {
        throw new Error(
          data.message ||
            "Interview could not be started"
        );
      }

      setSessionId(data.session_id);
      setQuestion(data.question || "");
      setQuestionNumber(
        data.question_number || 1
      );

      setInterviewStarted(true);
      setInterviewEnded(false);
      setReport(null);
      setTranscribedAnswer("");

      speakQuestion(data.question);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Camera, microphone, or backend connection failed."
      );
    }
  };

  // =========================================================
  // START RECORDING
  // =========================================================

  const startRecording = () => {
    if (speaking || processing) {
      return;
    }

    try {
      const stream =
        videoRef.current?.srcObject;

      if (!stream) {
        setError(
          "Camera and microphone are not active."
        );
        return;
      }

      audioChunksRef.current = [];

      const audioStream = new MediaStream(
        stream.getAudioTracks()
      );

      let recorder;

      if (
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus"
        )
      ) {
        recorder = new MediaRecorder(
          audioStream,
          {
            mimeType:
              "audio/webm;codecs=opus",
          }
        );
      } else if (
        MediaRecorder.isTypeSupported(
          "audio/webm"
        )
      ) {
        recorder = new MediaRecorder(
          audioStream,
          {
            mimeType: "audio/webm",
          }
        );
      } else {
        recorder =
          new MediaRecorder(audioStream);
      }

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(
            event.data
          );
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: recorder.mimeType,
          }
        );

        console.log(
          "Audio size:",
          audioBlob.size
        );

        await sendVoiceAnswer(audioBlob);
      };

      recorder.start();

      setRecording(true);
      setError("");
      setTranscribedAnswer("");

    } catch (err) {
      console.error(err);

      setError(
        "Unable to start voice recording."
      );
    }
  };

  // =========================================================
  // STOP RECORDING
  // =========================================================

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !==
        "inactive"
    ) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  // =========================================================
  // SEND VOICE ANSWER
  // =========================================================

  const sendVoiceAnswer = async (
    audioBlob
  ) => {
    try {
      setProcessing(true);
      setError("");

      const formData = new FormData();

      formData.append(
        "session_id",
        sessionId
      );

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
        const errorText =
          await response.text();

        console.error(
          "Voice answer error:",
          errorText
        );

        throw new Error(
          `Voice answer failed: ${response.status}`
        );
      }

      const data =
        await response.json();

      console.log(
        "VOICE ANSWER RESPONSE:",
        data
      );

      if (data.status !== "success") {
        throw new Error(
          data.message ||
            "Voice answer processing failed."
        );
      }

      setTranscribedAnswer(
        data.transcribed_answer || ""
      );

      // Get next question
      if (data.next_question) {
        const nextQuestion =
          data.next_question.question ||
          data.next_question ||
          "";

        setQuestion(nextQuestion);

        setQuestionNumber(
          (previous) =>
            previous + 1
        );

        speakQuestion(nextQuestion);
      }

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to process answer."
      );

    } finally {
      setProcessing(false);
    }
  };

  // =========================================================
  // OPEN END INTERVIEW CONFIRMATION
  // =========================================================

  const endInterview = () => {
    console.log(
      "END INTERVIEW BUTTON CLICKED"
    );

    if (!sessionId) {
      setError(
        "There is no active interview session."
      );
      return;
    }

    if (recording) {
      setError(
        "Please stop recording before ending the interview."
      );
      return;
    }

    setShowEndConfirmation(true);
  };

  // =========================================================
  // ACTUALLY END INTERVIEW
  // =========================================================

  const confirmEndInterview =
    async () => {
      console.log(
        "CONFIRM END INTERVIEW"
      );

      setShowEndConfirmation(false);

      try {
        setProcessing(true);
        setError("");

        // Stop EDITH speech
        window.speechSynthesis.cancel();
        setSpeaking(false);

        const response =
          await fetch(
            `http://127.0.0.1:8000/interview/end/${sessionId}`,
            {
              method: "POST",
            }
          );

        const data =
          await response.json();

        console.log(
          "END INTERVIEW RESPONSE:",
          data
        );

        if (!response.ok) {
          throw new Error(
            data.detail ||
              "Failed to end interview."
          );
        }

        if (
          data.status !== "success"
        ) {
          throw new Error(
            data.message ||
              "Interview could not be completed."
          );
        }

        // Save report
        setReport(data.report);

        // Stop camera and microphone
        const stream =
          videoRef.current?.srcObject;

        if (stream) {
          stream
            .getTracks()
            .forEach((track) => {
              track.stop();
            });

          videoRef.current.srcObject =
            null;
        }

        setInterviewStarted(false);
        setInterviewEnded(true);

      } catch (err) {
        console.error(err);

        setError(
          err.message ||
            "Unable to generate interview report."
        );

      } finally {
        setProcessing(false);
      }
    };

  // =========================================================
  // START NEW INTERVIEW
  // =========================================================

  const startNewInterview = () => {
    setSessionId("");
    setQuestion("");
    setQuestionNumber(0);

    setRecording(false);
    setProcessing(false);
    setSpeaking(false);

    setTranscribedAnswer("");

    setInterviewStarted(false);
    setInterviewEnded(false);

    setReport(null);
    setError("");

    setShowEndConfirmation(false);
  };

  // =========================================================
  // REPORT SCREEN
  // =========================================================

  if (
    interviewEnded &&
    report
  ) {
    return (
      <div className="app">

        <header className="header">

          <div>
            <h1>EDITH</h1>

            <p>
              AI Interview & Placement Coach
            </p>
          </div>

          <div className="status">

            <span className="status-dot"></span>

            Interview Completed

          </div>

        </header>

        <main className="dashboard">

          <section className="welcome">

            <h2>
              Interview Completed
            </h2>

            <p>
              EDITH has analyzed your
              interview performance.
            </p>

          </section>

          <div className="report-container">

            <pre className="report-output">
              {JSON.stringify(
                report,
                null,
                2
              )}
            </pre>

          </div>

          <div className="new-interview-container">

            <button
              className="start-button"
              onClick={
                startNewInterview
              }
            >
              🎤 Start New Interview
            </button>

          </div>

        </main>

        <footer>

          <p>
            EDITH • Adaptive AI Interview System
          </p>

        </footer>

      </div>
    );
  }

  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div>

          <h1>EDITH</h1>

          <p>
            AI Interview & Placement Coach
          </p>

        </div>

        <div className="status">

          <span className="status-dot"></span>

          {interviewStarted
            ? "Interview Active"
            : backendStatus}

        </div>

      </header>


      {/* MAIN */}

      <main className="dashboard">

        {/* WELCOME */}

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


        {/* PREPARATION CARDS */}

        {!interviewStarted && (

          <section className="cards">

            <div className="card">

              <h3>
                📄 Resume
              </h3>

              <p>
                Upload your resume to create
                a personalized interview.
              </p>

              <button>
                Upload Resume
              </button>

            </div>


            <div className="card">

              <h3>
                💼 Job Role
              </h3>

              <p>
                Select the role you want
                to prepare for.
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

              <h3>
                🎯 Interview Type
              </h3>

              <p>
                Choose the type of
                interview you want to practice.
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


        {/* CAMERA + INTERVIEW */}

        <section className="camera-section">

          {/* CAMERA */}

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
                  Your camera will appear
                  here during the interview.
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


          {/* INTERVIEW PANEL */}

          <div className="interview-panel">

            <h2>

              {interviewStarted
                ? "Interview in Progress"
                : "Ready for your interview?"}

            </h2>


            {/* ACTIVE INTERVIEW */}

            {interviewStarted && (

              <>

                {/* QUESTION */}

                <div className="question-box">

                  <div className="question-header">

                    <span>
                      Question{" "}
                      {questionNumber}
                    </span>

                    {speaking && (

                      <span className="speaking-label">
                        🔊 EDITH speaking
                      </span>

                    )}

                  </div>


                  {/* PROGRESS */}

                  <div className="question-progress">

                    <div
                      className="question-progress-bar"
                      style={{
                        width: `${Math.min(
                          questionNumber *
                            10,
                          100
                        )}%`,
                      }}
                    ></div>

                  </div>


                  <h3>
                    {question}
                  </h3>

                </div>


                {/* SESSION */}

                <div className="session-info">

                  <span>
                    🟢 Session Active
                  </span>

                  <span>
                    Session:{" "}
                    {sessionId
                      ? `${sessionId.slice(
                          0,
                          8
                        )}...`
                      : ""}
                  </span>

                </div>


                {/* VOICE STATUS */}

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


                {/* =================================================
                    SEPARATED CONTROLS
                    ================================================= */}

                <div className="voice-controls">

                  {/* ANSWER CONTROL */}

                  <div className="answer-control-group">

                    {!recording &&
                      !processing &&
                      !speaking && (

                        <button
                          type="button"
                          className="start-button"
                          onClick={
                            startRecording
                          }
                          disabled={
                            !interviewStarted
                          }
                        >
                          🎤 Start Answer
                        </button>

                      )}


                    {recording && (

                      <button
                        type="button"
                        className="start-button"
                        onClick={
                          stopRecording
                        }
                      >
                        ⏹ Stop Recording
                      </button>

                    )}

                  </div>


                  {/* END INTERVIEW CONTROL */}

                  <div className="end-control-group">

                    {!recording &&
                      !processing && (

                        <button
                          type="button"
                          className="end-interview-button"
                          onClick={
                            endInterview
                          }
                        >
                          🛑 End Interview
                        </button>

                      )}

                  </div>

                </div>


                {/* TRANSCRIPTION */}

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


            {/* BEFORE INTERVIEW */}

            {!interviewStarted && (

              <>

                <p>
                  EDITH will analyze your
                  answers, communication,
                  technical knowledge and
                  identify areas for
                  improvement.
                </p>

                <button
                  type="button"
                  className="start-button"
                  onClick={
                    startInterview
                  }
                >
                  🎤 Start Interview
                </button>

              </>

            )}


            {/* ERROR */}

            {error && (

              <p className="error-message">
                {error}
              </p>

            )}

          </div>

        </section>

      </main>


      {/* FOOTER */}

      <footer>

        <p>
          EDITH • Adaptive AI Interview System
        </p>

      </footer>


      {/* =========================================================
          END INTERVIEW CONFIRMATION MODAL
          ========================================================= */}

      {showEndConfirmation && (

        <div className="confirmation-overlay">

          <div className="confirmation-modal">

            <div className="confirmation-icon">
              🛑
            </div>

            <h2>
              End Interview?
            </h2>

            <p>
              Are you sure you want to end
              this interview and generate
              your performance report?
            </p>

            <div className="confirmation-buttons">

              <button
                type="button"
                className="continue-button"
                onClick={() =>
                  setShowEndConfirmation(
                    false
                  )
                }
              >
                Continue Interview
              </button>

              <button
                type="button"
                className="confirm-end-button"
                onClick={
                  confirmEndInterview
                }
              >
                🛑 End Interview
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}

export default App;
