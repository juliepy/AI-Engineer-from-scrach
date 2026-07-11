"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarPlus } from "lucide-react";
import { createMeeting, fetchContacts, type ContactOut } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";

const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Berlin",
  "Europe/Paris",
  "Asia/Tokyo",
  "Asia/Singapore",
  "Australia/Sydney",
];

export default function SchedulePage() {
  const router = useRouter();
  const [contacts, setContacts] = useState<ContactOut[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [title, setTitle] = useState("");
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [durationMins, setDurationMins] = useState("30");
  const [timezone, setTimezone] = useState("UTC");
  const [notes, setNotes] = useState("");
  const [selectedContacts, setSelectedContacts] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchContacts().then(setContacts).catch(() => null);
  }, []);

  function toggleContact(id: number) {
    setSelectedContacts((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!title || !startDate) {
      setError("Title and start date are required.");
      return;
    }
    setSaving(true);
    try {
      const start = new Date(`${startDate}T${startTime}:00`);
      const end = new Date(start.getTime() + Number(durationMins) * 60 * 1000);
      const created = await createMeeting({
        title,
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        meeting_timezone: timezone,
        notes: notes || undefined,
        invitee_contact_ids: Array.from(selectedContacts),
      });
      router.push(`/meetings/${created.id}`);
    } catch {
      setError("Failed to schedule meeting. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell title="Schedule Meeting">
      <div className="max-w-2xl">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CalendarPlus className="h-5 w-5 text-brand" />
              <CardTitle>New Meeting</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && <Alert variant="error">{error}</Alert>}

              <div className="space-y-1.5">
                <Label htmlFor="title">Meeting Title *</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Discovery Call with Acme Corp"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="time">Time *</Label>
                  <Input
                    id="time"
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="duration">Duration</Label>
                  <Select
                    id="duration"
                    value={durationMins}
                    onChange={(e) => setDurationMins(e.target.value)}
                  >
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="45">45 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="90">1.5 hours</option>
                    <option value="120">2 hours</option>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="tz">Timezone</Label>
                  <Select
                    id="tz"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                  >
                    {TIMEZONES.map((tz) => (
                      <option key={tz} value={tz}>{tz}</option>
                    ))}
                  </Select>
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Agenda, context, talking points…"
                  rows={3}
                />
              </div>

              {/* Contact selection */}
              <div className="space-y-2">
                <Label>Invite Contacts</Label>
                {contacts.length === 0 ? (
                  <p className="text-sm text-gray-400">No contacts yet.</p>
                ) : (
                  <div className="border border-gray-200 rounded-lg overflow-hidden max-h-48 overflow-y-auto">
                    {contacts.map((c) => (
                      <label
                        key={c.id}
                        className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0"
                      >
                        <input
                          type="checkbox"
                          checked={selectedContacts.has(c.id)}
                          onChange={() => toggleContact(c.id)}
                          className="rounded accent-brand"
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{c.name}</p>
                          <p className="text-xs text-gray-500">{c.company ? `${c.company} · ` : ""}{c.email}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
                {selectedContacts.size > 0 && (
                  <p className="text-xs text-gray-500">{selectedContacts.size} contact{selectedContacts.size !== 1 ? "s" : ""} selected</p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <Button type="submit" disabled={saving}>
                  {saving ? "Scheduling…" : "Schedule Meeting"}
                </Button>
                <Button type="button" variant="secondary" onClick={() => router.push("/meetings")}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
