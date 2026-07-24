import { useState, type FormEvent } from "react";
import { ApiError } from "../api/client";
import { useCreateLink } from "../hooks/useLinks";
import type { Link } from "../types/link";
import { CopyButton } from "./CopyButton";
import { ErrorBanner } from "./ErrorBanner";

export function ShortenForm() {
  const [originalUrl, setOriginalUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [createdLink, setCreatedLink] = useState<Link | null>(null);

  const createLink = useCreateLink();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCreatedLink(null);

    const result = await createLink.mutateAsync({
      original_url: originalUrl,
      custom_alias: customAlias.trim() === "" ? undefined : customAlias.trim(),
      expires_at: expiresAt === "" ? undefined : new Date(expiresAt).toISOString(),
    });

    setCreatedLink(result);
    setOriginalUrl("");
    setCustomAlias("");
    setExpiresAt("");
  };

  const errorMessage =
    createLink.error instanceof ApiError ? createLink.error.displayMessage : null;

  return (
    <div className="card">
      <h2>Shorten a URL</h2>
      <form onSubmit={handleSubmit} className="shorten-form">
        <label htmlFor="original_url">Destination URL</label>
        <input
          id="original_url"
          type="url"
          required
          placeholder="https://example.com/some/long/path"
          value={originalUrl}
          onChange={(event) => setOriginalUrl(event.target.value)}
        />

        <label htmlFor="custom_alias">Custom alias (optional)</label>
        <input
          id="custom_alias"
          type="text"
          placeholder="my-link"
          minLength={3}
          maxLength={16}
          value={customAlias}
          onChange={(event) => setCustomAlias(event.target.value)}
        />

        <label htmlFor="expires_at">Expires at (optional)</label>
        <input
          id="expires_at"
          type="datetime-local"
          value={expiresAt}
          onChange={(event) => setExpiresAt(event.target.value)}
        />

        <button type="submit" disabled={createLink.isPending}>
          {createLink.isPending ? "Shortening..." : "Shorten"}
        </button>
      </form>

      {errorMessage !== null ? <ErrorBanner message={errorMessage} /> : null}

      {createdLink !== null ? (
        <div className="result">
          <a href={createdLink.short_url} target="_blank" rel="noreferrer">
            {createdLink.short_url}
          </a>
          <CopyButton value={createdLink.short_url} />
        </div>
      ) : null}
    </div>
  );
}
