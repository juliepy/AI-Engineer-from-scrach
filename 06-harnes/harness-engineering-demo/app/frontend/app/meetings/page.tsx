"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, Filter, Download, Plus, ChevronLeft, ChevronRight } from "lucide-react";
import {
  fetchMeetings,
  fetchTeam,
  exportUrl,
  type MeetingRow,
  type TeamMember,
} from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { PageSpinner } from "@/components/ui/spinner";
import { EmptyState } from "@/components/ui/empty-state";

const PAGE_SIZE = 20;

function statusBadge(status: string) {
  if (status === "completed") return <Badge variant="success">Completed</Badge>;
  if (status === "cancelled") return <Badge variant="danger">Cancelled</Badge>;
  return <Badge variant="info">Scheduled</Badge>;
}

export default function MeetingsPage() {
  const [rows, setRows] = useState<MeetingRow[]>([]);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  // Filter state
  const [search, setSearch] = useState("");
  const [hostId, setHostId] = useState("");
  const [status, setStatus] = useState("");
  const [startAfter, setStartAfter] = useState("");
  const [startBefore, setStartBefore] = useState("");
  const [page, setPage] = useState(0);

  function load() {
    setLoading(true);
    fetchMeetings({
      search: search || undefined,
      host_id: hostId ? Number(hostId) : undefined,
      status: status || undefined,
      start_after: startAfter || undefined,
      start_before: startBefore || undefined,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    })
      .then(setRows)
      .catch(() => setError("Could not load meetings"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    setMounted(true);
    fetchTeam().then((t) => setMembers(t.members)).catch(() => null);
  }, []);

  useEffect(() => {
    load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, hostId, status, startAfter, startBefore, page]);

  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPage(0);
    load();
  }

  return (
    <AppShell
      title="Meetings"
      actions={
        <Link href="/schedule">
          <Button size="sm">
            <Plus className="h-4 w-4" />
            Schedule
          </Button>
        </Link>
      }
    >
      {/* Filters */}
      <Card className="mb-4">
        <div className="p-4 flex flex-wrap gap-3 items-end">
          <form onSubmit={handleSearch} className="flex gap-2 flex-1 min-w-[200px]">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                className="pl-8"
                placeholder="Search meetings…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </form>

          <Select value={hostId} onChange={(e) => { setHostId(e.target.value); setPage(0); }} className="w-40">
            <option value="">All hosts</option>
            {members.map((m) => (
              <option key={m.id} value={String(m.id)}>{m.name}</option>
            ))}
          </Select>

          <Select value={status} onChange={(e) => { setStatus(e.target.value); setPage(0); }} className="w-36">
            <option value="">All statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </Select>

          <div className="flex gap-2 items-center">
            <Input
              type="date"
              value={startAfter}
              onChange={(e) => { setStartAfter(e.target.value ? e.target.value + "T00:00:00Z" : ""); setPage(0); }}
              className="w-36"
              title="Start after"
            />
            <span className="text-gray-400 text-sm">–</span>
            <Input
              type="date"
              value={startBefore}
              onChange={(e) => { setStartBefore(e.target.value ? e.target.value + "T23:59:59Z" : ""); setPage(0); }}
              className="w-36"
              title="Start before"
            />
          </div>

          <div className="flex gap-2 ml-auto">
            {/* Only PDF export exists today. SCH-142 adds CSV — the workshop builds it live. */}
            {/* Gated on mount: exportUrl() reads the auth token from localStorage, which is
                absent during SSR — rendering the tokenized href before mount mismatches hydration. */}
            {mounted ? (
              <a href={exportUrl("pdf")} target="_blank" rel="noreferrer">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4" />
                  Export PDF
                </Button>
              </a>
            ) : (
              <Button variant="outline" size="sm" disabled>
                <Download className="h-4 w-4" />
                Export PDF
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card>
        {loading ? (
          <PageSpinner />
        ) : error ? (
          <div className="p-6 text-red-600 text-sm">{error}</div>
        ) : rows.length === 0 ? (
          <EmptyState
            title="No meetings found"
            description="Try adjusting your filters or schedule a new meeting."
            action={
              <Link href="/schedule">
                <Button size="sm">
                  <Plus className="h-4 w-4" />
                  Schedule Meeting
                </Button>
              </Link>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="schedulr-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Host</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>TZ</th>
                  <th>Status</th>
                  <th>Invitees</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium">
                      <Link href={`/meetings/${m.id}`} className="hover:text-brand">
                        {m.title}
                      </Link>
                    </td>
                    <td className="text-gray-600">{m.host}</td>
                    <td className="text-gray-600 whitespace-nowrap text-xs">{m.start}</td>
                    <td className="text-gray-600 whitespace-nowrap text-xs">{m.end}</td>
                    <td className="text-gray-500 text-xs">{m.timezone}</td>
                    <td>{statusBadge(m.status)}</td>
                    <td className="text-gray-500">{m.inviteeCount}</td>
                    <td>
                      <Link href={`/meetings/${m.id}`}>
                        <Button variant="ghost" size="sm">View</Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!loading && rows.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
            <span className="text-xs text-gray-500">
              Page {page + 1}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={rows.length < PAGE_SIZE}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
