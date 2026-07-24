import { useState } from "react";
import { LinkTable } from "../components/LinkTable";
import { useLinks } from "../hooks/useLinks";

const PAGE_SIZE = 20;

export function DashboardPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useLinks(page, PAGE_SIZE);

  if (isLoading) {
    return <p className="analytics-status">Loading links...</p>;
  }

  if (isError || data === undefined) {
    return <p className="analytics-status">Could not load links.</p>;
  }

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));

  return (
    <section className="card">
      <h2>Your links</h2>
      <LinkTable links={data.items} />
      <div className="pagination">
        <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          type="button"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </button>
      </div>
    </section>
  );
}
