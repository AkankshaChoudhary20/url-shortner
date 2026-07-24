import { Fragment, useState } from "react";
import type { Link } from "../types/link";
import { CopyButton } from "./CopyButton";
import { ExpiryBadge } from "./ExpiryBadge";
import { LinkAnalyticsPanel } from "./LinkAnalyticsPanel";

interface LinkTableProps {
  links: Link[];
}

export function LinkTable({ links }: LinkTableProps) {
  const [expandedCode, setExpandedCode] = useState<string | null>(null);

  if (links.length === 0) {
    return <p className="analytics-status">No links yet. Shorten one to get started.</p>;
  }

  return (
    <div className="link-table-wrapper">
      <table className="link-table">
        <thead>
          <tr>
            <th>Short link</th>
            <th>Destination</th>
            <th>Clicks</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {links.map((link) => (
            <Fragment key={link.short_code}>
              <tr>
                <td>
                  <a href={link.short_url} target="_blank" rel="noreferrer">
                    {link.short_url}
                  </a>
                  <CopyButton value={link.short_url} />
                </td>
                <td className="destination-cell" title={link.original_url}>
                  {link.original_url}
                </td>
                <td>{link.click_count}</td>
                <td>
                  <ExpiryBadge expiresAt={link.expires_at} isExpired={link.is_expired} />
                </td>
                <td>
                  <button
                    type="button"
                    onClick={() =>
                      setExpandedCode(expandedCode === link.short_code ? null : link.short_code)
                    }
                  >
                    {expandedCode === link.short_code ? "Hide analytics" : "View analytics"}
                  </button>
                </td>
              </tr>
              {expandedCode === link.short_code ? (
                <tr>
                  <td colSpan={5}>
                    <LinkAnalyticsPanel shortCode={link.short_code} />
                  </td>
                </tr>
              ) : null}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
