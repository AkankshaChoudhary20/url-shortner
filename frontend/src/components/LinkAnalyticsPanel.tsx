import { useLinkAnalytics } from "../hooks/useLinks";

interface LinkAnalyticsPanelProps {
  shortCode: string;
}

export function LinkAnalyticsPanel({ shortCode }: LinkAnalyticsPanelProps) {
  const { data, isLoading, isError } = useLinkAnalytics(shortCode);

  if (isLoading) {
    return <p className="analytics-status">Loading analytics...</p>;
  }

  if (isError || data === undefined) {
    return <p className="analytics-status">Could not load analytics.</p>;
  }

  return (
    <div className="analytics-panel">
      <p>
        Total clicks: <strong>{data.total_clicks}</strong>
      </p>
      {data.clicks_by_day.length === 0 ? (
        <p className="analytics-status">No clicks yet.</p>
      ) : (
        <ul className="click-buckets">
          {data.clicks_by_day.map((bucket) => (
            <li key={bucket.day}>
              <span>{bucket.day}</span>
              <span>{bucket.clicks} clicks</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
