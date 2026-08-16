import React from "react";
import "./InterviewReport.css";

function InterviewReport({ report }) {
  if (!report) {
    return (
      <div className="report-container">
        <h2>No interview report available</h2>
      </div>
    );
  }

  return (
    <div className="report-container">

      <div className="report-header">
        <h1>EDITH Interview Report</h1>

        <div className="summary-grid">

          <div className="summary-card">
            <span>Overall Score</span>
            <strong>
              {report.overall_score}/10
            </strong>
          </div>

          <div className="summary-card">
            <span>Performance</span>
            <strong>
              {report.performance_level}
            </strong>
          </div>

          <div className="summary-card">
            <span>Total Questions</span>
            <strong>
              {report.total_questions}
            </strong>
          </div>

        </div>
      </div>


      <section className="report-section">

        <h2>Question-by-Question Evaluation</h2>

        {report.question_reports?.map(
          (item) => (

            <div
              className="question-card"
              key={item.question_number}
            >

              <div className="question-header">

                <h3>
                  Question {item.question_number}
                </h3>

                <span className="score">
                  {item.score}/10
                </span>

              </div>


              <div className="question-content">

                <h4>Question</h4>

                <p>
                  {item.question}
                </p>


                <h4>Candidate Answer</h4>

                <p>
                  {item.answer}
                </p>

              </div>


              <div className="metrics">

                <div>
                  <span>Correctness</span>
                  <strong>
                    {item.correctness}/10
                  </strong>
                </div>

                <div>
                  <span>Relevance</span>
                  <strong>
                    {item.relevance}/10
                  </strong>
                </div>

                <div>
                  <span>Technical Understanding</span>
                  <strong>
                    {item.technical_understanding}/10
                  </strong>
                </div>

                <div>
                  <span>Completeness</span>
                  <strong>
                    {item.completeness}/10
                  </strong>
                </div>

                <div>
                  <span>Reasoning</span>
                  <strong>
                    {item.reasoning}/10
                  </strong>
                </div>

              </div>


              <div className="evaluation-block">

                <h4>✓ Strengths</h4>

                {item.strengths?.length ? (

                  <ul>
                    {item.strengths.map(
                      (strength, index) => (
                        <li key={index}>
                          {strength}
                        </li>
                      )
                    )}
                  </ul>

                ) : (

                  <p>None identified.</p>

                )}

              </div>


              <div className="evaluation-block">

                <h4>• Missing Points</h4>

                {item.missing_points?.length ? (

                  <ul>
                    {item.missing_points.map(
                      (point, index) => (
                        <li key={index}>
                          {point}
                        </li>
                      )
                    )}
                  </ul>

                ) : (

                  <p>None identified.</p>

                )}

              </div>


              <div className="evaluation-block">

                <h4>⚠ Misconceptions</h4>

                {item.misconceptions?.length ? (

                  <ul>
                    {item.misconceptions.map(
                      (item, index) => (
                        <li key={index}>
                          {item}
                        </li>
                      )
                    )}
                  </ul>

                ) : (

                  <p>None identified.</p>

                )}

              </div>


              <div className="feedback">

                <h4>Interviewer Feedback</h4>

                <p>
                  {item.feedback}
                </p>

              </div>

            </div>

          )
        )}

      </section>


      <section className="report-section">

        <h2>Overall Strengths</h2>

        {report.strengths?.length ? (

          <ul>
            {report.strengths.map(
              (strength, index) => (
                <li key={index}>
                  {strength}
                </li>
              )
            )}
          </ul>

        ) : (

          <p>No major strengths identified.</p>

        )}

      </section>


      <section className="report-section">

        <h2>Areas to Improve</h2>

        {report.missing_points?.length ? (

          <ul>
            {report.missing_points.map(
              (point, index) => (
                <li key={index}>
                  {point}
                </li>
              )
            )}
          </ul>

        ) : (

          <p>No major missing points identified.</p>

        )}

      </section>


      <section className="report-section">

        <h2>Technical Misconceptions</h2>

        {report.misconceptions?.length ? (

          <ul>
            {report.misconceptions.map(
              (item, index) => (
                <li key={index}>
                  {item}
                </li>
              )
            )}
          </ul>

        ) : (

          <p>No technical misconceptions identified.</p>

        )}

      </section>

    </div>
  );
}

export default InterviewReport;