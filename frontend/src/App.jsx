import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [approved, setApproved] = useState(false);
  const [rejected, setRejected] = useState(false);

  const [reviewOpen, setReviewOpen] = useState(false);
  const [auditLogs, setAuditLogs] = useState([]);

  const [rejectionReason, setRejectionReason] = useState("");

  const handleApproval = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/incidents/1/approve",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Approval failed");
      }

      setApproved(true);
      setReviewOpen(false);
      loadAuditLogs();
    } catch (error) {
      console.error(error);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      return;
    }

    try {
      const response = await fetch(
  "http://127.0.0.1:8000/api/incidents/1/reject",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      reason: rejectionReason.trim(),
    }),
  }
);

      if (!response.ok) {
        throw new Error("Rejection failed");
      }

      setRejected(true);
      setReviewOpen(false);
      loadAuditLogs();
    } catch (error) {
      console.error(error);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/incidents/1/audit-logs"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch audit logs");
      }

      const data = await response.json();
      setAuditLogs(data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/investigate")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch investigation data");
        }

        return response.json();
      })
      .then((data) => {
        setInvestigation(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });

    loadAuditLogs();
  }, []);

  if (loading) {
    return <div className="app">Loading InfraPilot...</div>;
  }

  if (error) {
    return (
      <div className="app">
        <div className="error-box">
          <h2>Unable to connect to InfraPilot API</h2>
          <p>{error}</p>
          <p>
            Make sure the FastAPI backend is running on port 8000.
          </p>
        </div>
      </div>
    );
  }

  const diagnosis = investigation?.diagnosis;
  const evidence = diagnosis?.evidence || [];
  const slowQueries = investigation?.evidence?.slow_queries || [];
  const deployments = investigation?.evidence?.deployments || [];

  const chartData = slowQueries
    .slice()
    .reverse()
    .map((query, index) => ({
      name: `Sample ${index + 1}`,
      latency: query.db_query_latency_ms,
    }));

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>InfraPilot</h1>
          <p>AI-powered incident investigation</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Connected
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <p className="eyebrow">INCIDENT INVESTIGATION</p>

            <h2>Why is the application slow?</h2>

            <p className="hero-text">
              InfraPilot correlates application, database and deployment
              signals to identify the most probable cause.
            </p>
          </div>

          <div className="confidence-card">
            <span>Confidence</span>
            <strong>{diagnosis?.confidence}</strong>
          </div>
        </section>

        <section className="summary-grid">
          <div className="summary-card danger">
            <span>Probable Cause</span>

            <h3>{diagnosis?.probable_cause}</h3>
          </div>

          <div className="summary-card">
            <span>Blast Radius</span>

            <h3>{diagnosis?.blast_radius}</h3>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">EVIDENCE</p>
              <h2>What InfraPilot found</h2>
            </div>
          </div>

          <div className="evidence-list">
            {evidence.map((item, index) => (
              <div className="evidence-card" key={index}>
                <div className="evidence-type">{item.type}</div>

                <div>
                  <strong>{item.source}</strong>

                  <p>{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">DATABASE PERFORMANCE</p>
              <h2>Slow query latency</h2>
            </div>
          </div>

          <div className="panel chart-panel">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="name" />

                <YAxis />

                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="latency"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">DEPLOYMENT TIMELINE</p>
              <h2>Recent deployments</h2>
            </div>
          </div>

          <div className="evidence-list">
            {deployments.map((deployment) => (
              <div className="evidence-card" key={deployment.id}>
                <div className="evidence-type">DEPLOYED</div>

                <div>
                  <strong>{deployment.version}</strong>

                  <p>{deployment.change_summary}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="two-column">
          <div className="panel">
            <p className="eyebrow">REMEDIATION</p>

            <h2>Recommended action</h2>

            <p>{diagnosis?.remediation}</p>
          </div>

          <div className="panel">
            <p className="eyebrow">ROLLBACK PLAN</p>

            <h2>Human approval required</h2>

            <p>{diagnosis?.rollback_plan}</p>

            {reviewOpen && (
              <div className="review-panel">
                <h3>Review Recommendation</h3>

                <p>
                  Please review the recommended action before approving it.
                </p>

                <textarea
                  className="rejection-reason"
                  placeholder="If rejecting, briefly explain why..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  maxLength={500}
                />

                <div className="review-actions">
                  <button
                    className="approval-button"
                    onClick={handleApproval}
                    disabled={approved}
                  >
                    {approved ? "Approved ✓" : "Approve"}
                  </button>

                  <button
                    className="reject-button"
                    onClick={handleReject}
                    disabled={false}
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}

            <button
              className="approval-button"
              onClick={() => setReviewOpen(true)}
              disabled={approved}
            >
              {approved ? "Approved ✓" : "Review & Approve"}
            </button>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">AUDIT LOG</p>
              <h2>Approval history</h2>
            </div>
          </div>

          <div className="evidence-list">
            {auditLogs.map((log) => (
              <div className="evidence-card" key={log.id}>
                <div className="evidence-type">{log.action}</div>

                <div>
                  <strong>{log.actor}</strong>

                  <p>
  {log.action === "REJECTED"
    ? `Rejection recorded at ${new Date(log.created_at).toLocaleString()}`
    : `Approval recorded at ${new Date(log.created_at).toLocaleString()}`}
</p>

{log.action === "REJECTED" && log.details && (
  <p>
    <strong>Reason:</strong>{" "}
    {typeof log.details === "string"
      ? JSON.parse(log.details).reason
      : log.details.reason}
  </p>
)}

                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">INVESTIGATION DATA</p>

              <h2>Database signals</h2>
            </div>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <span>Slow Query Samples</span>

              <strong>
                {investigation?.evidence?.slow_queries?.length || 0}
              </strong>
            </div>

            <div className="metric-card">
              <span>Deployments Checked</span>

              <strong>
                {investigation?.evidence?.deployments?.length || 0}
              </strong>
            </div>

            <div className="metric-card">
              <span>Query Plan</span>

              <strong>
                {investigation?.evidence?.query_plan?.length || 0} lines
              </strong>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;