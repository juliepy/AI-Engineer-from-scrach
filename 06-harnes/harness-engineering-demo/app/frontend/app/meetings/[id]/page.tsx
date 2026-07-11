"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, User, Clock, Globe, Edit2, Trash2, CheckCircle, XCircle, Minus } from "lucide-react";
import {
  getMeeting,
  updateMeeting,
  cancelMeeting,
  updateRSVP,
  type MeetingRow,
} from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { PageSpinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";

function statusBadge(status: string) {
  if (status === "completed") return <Badge variant="success">Completed</Badge>;
  if (status === "cancelled") return <Badge variant="danger">Cancelled</Badge>;
  return <Badge variant="info">Scheduled</Badge>;
}

function rsvpBadge(response: string) {
  if (response === "accepted") return <Badge variant="success">Accepted</Badge>;
  if (response === "declined") return <Badge variant="danger">Declined</Badge>;
  return <Badge variant="default">Pending</Badge>;
}

export default function MeetingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [meeting, setMeeting] = useState<MeetingRow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    getMeeting(Number(id))
      .then((m) => {
        setMeeting(m);
        setNotes(m.notes ?? "");
      })
      .catch(() => setError("Meeting not found"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, [id]);

  async function handleSaveNotes() {
    if (!meeting) return;
    setSaving(true);
    try {
      const updated = await updateMeeting(meeting.id, { notes });
      setMeeting(updated);
      setEditingNotes(false);
    } catch {
      setError("Failed to save notes");
    } finally {
      setSaving(false);
    }
  }

  async function handleCancel() {
    if (!meeting || !confirm("Cancel this meeting?")) return;
    try {
      await cancelMeeting(meeting.id);
      router.push("/meetings");
    } catch {
      setError("Failed to cancel meeting");
    }
  }

  async function handleMarkComplete() {
    if (!meeting) return;
    try {
      const updated = await updateMeeting(meeting.id, { status: "completed" });
      setMeeting(updated);
    } catch {
      setError("Failed to update status");
    }
  }

  async function handleRSVP(inviteeId: number, response: string) {
    if (!meeting) return;
    try {
      await updateRSVP(meeting.id, inviteeId, response);
      load();
    } catch {
      setError("Failed to update RSVP");
    }
  }

  if (loading) return <AppShell title="Meeting"><PageSpinner /></AppShell>;
  if (error || !meeting) return (
    <AppShell title="Meeting">
      <Alert variant="error">{error ?? "Meeting not found"}</Alert>
    </AppShell>
  );

  return (
    <AppShell title="Meeting Detail">
      <div className="mb-4">
        <Link href="/meetings" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4" />
          Back to meetings
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{meeting.title}</h2>
                  <div className="mt-2">{statusBadge(meeting.status)}</div>
                </div>
                <div className="flex gap-2">
                  {meeting.status === "scheduled" && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleMarkComplete}
                      >
                        <CheckCircle className="h-4 w-4" />
                        Mark Complete
                      </Button>
                      <Button variant="danger-outline" size="sm" onClick={handleCancel}>
                        <XCircle className="h-4 w-4" />
                        Cancel
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-gray-500 text-xs">Start</p>
                    <p className="font-medium text-gray-900">{meeting.start}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-gray-500 text-xs">End</p>
                    <p className="font-medium text-gray-900">{meeting.end}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <User className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-gray-500 text-xs">Host</p>
                    <p className="font-medium text-gray-900">{meeting.host}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Globe className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-gray-500 text-xs">Timezone</p>
                    <p className="font-medium text-gray-900">{meeting.timezone}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Notes</CardTitle>
                {!editingNotes && (
                  <Button variant="ghost" size="sm" onClick={() => setEditingNotes(true)}>
                    <Edit2 className="h-4 w-4" />
                    Edit
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {editingNotes ? (
                <div className="space-y-3">
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={5}
                    placeholder="Add meeting notes…"
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSaveNotes} disabled={saving}>
                      {saving ? "Saving…" : "Save"}
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => { setEditingNotes(false); setNotes(meeting.notes ?? ""); }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-600 whitespace-pre-wrap">
                  {meeting.notes || <span className="text-gray-400 italic">No notes yet.</span>}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Invitees */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Invitees ({meeting.inviteeCount})</CardTitle>
            </CardHeader>
            <CardContent>
              {meeting.invitees.length === 0 ? (
                <p className="text-sm text-gray-400">No invitees</p>
              ) : (
                <ul className="space-y-3">
                  {meeting.invitees.map((inv) => (
                    <li key={inv.id} className="flex items-start justify-between gap-2">
                      <div>
                        <Link
                          href={`/contacts/${inv.contact_id}`}
                          className="text-sm font-medium text-gray-900 hover:text-brand"
                        >
                          {inv.contact_name}
                        </Link>
                        <p className="text-xs text-gray-500">{inv.contact_email}</p>
                        <div className="mt-1">{rsvpBadge(inv.response)}</div>
                      </div>
                      <div className="flex gap-1 shrink-0">
                        <button
                          title="Accept"
                          onClick={() => handleRSVP(inv.id, "accepted")}
                          className="p-1 rounded hover:bg-green-50 text-green-600"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                        <button
                          title="Decline"
                          onClick={() => handleRSVP(inv.id, "declined")}
                          className="p-1 rounded hover:bg-red-50 text-red-500"
                        >
                          <XCircle className="h-4 w-4" />
                        </button>
                        <button
                          title="Reset"
                          onClick={() => handleRSVP(inv.id, "pending")}
                          className="p-1 rounded hover:bg-gray-100 text-gray-400"
                        >
                          <Minus className="h-4 w-4" />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
