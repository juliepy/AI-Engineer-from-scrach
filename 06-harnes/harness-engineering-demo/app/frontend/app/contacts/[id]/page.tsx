"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Edit2, Trash2, CalendarDays, Mail, Phone, Building2, Briefcase } from "lucide-react";
import {
  getContact,
  updateContact,
  deleteContact,
  fetchMeetings,
  type ContactOut,
  type MeetingRow,
} from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { PageSpinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";

const STAGES = ["lead", "prospect", "opportunity", "customer", "churned"];

function stageBadge(stage: string) {
  const map: Record<string, "default" | "info" | "warning" | "success" | "danger"> = {
    lead: "default", prospect: "info", opportunity: "warning", customer: "success", churned: "danger",
  };
  return <Badge variant={map[stage] ?? "default"}>{stage}</Badge>;
}

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [contact, setContact] = useState<ContactOut | null>(null);
  const [meetings, setMeetings] = useState<MeetingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editCompany, setEditCompany] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editStage, setEditStage] = useState("lead");

  function startEdit(c: ContactOut) {
    setEditName(c.name);
    setEditEmail(c.email);
    setEditCompany(c.company ?? "");
    setEditPhone(c.phone ?? "");
    setEditTitle(c.title ?? "");
    setEditNotes(c.notes ?? "");
    setEditStage(c.stage);
    setEditing(true);
  }

  useEffect(() => {
    Promise.all([
      getContact(Number(id)),
      fetchMeetings({ contact_id: Number(id) }),
    ]).then(([c, ms]) => {
      setContact(c);
      setMeetings(ms);
    }).catch(() => setError("Contact not found"))
    .finally(() => setLoading(false));
  }, [id]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!contact) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await updateContact(contact.id, {
        name: editName,
        email: editEmail,
        company: editCompany || undefined,
        phone: editPhone || undefined,
        title: editTitle || undefined,
        notes: editNotes || undefined,
        stage: editStage,
      });
      setContact(updated);
      setEditing(false);
    } catch {
      setError("Failed to save contact.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!contact || !confirm(`Delete ${contact.name}? This cannot be undone.`)) return;
    try {
      await deleteContact(contact.id);
      router.push("/contacts");
    } catch {
      setError("Failed to delete contact.");
    }
  }

  if (loading) return <AppShell title="Contact"><PageSpinner /></AppShell>;
  if (error || !contact) return <AppShell title="Contact"><Alert variant="error">{error ?? "Not found"}</Alert></AppShell>;

  return (
    <AppShell title="Contact Detail">
      <div className="mb-4">
        <Link href="/contacts" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4" />
          Back to contacts
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Contact info */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{contact.name}</h2>
                  <div className="mt-1 flex items-center gap-2">
                    {stageBadge(contact.stage)}
                    {contact.company && <span className="text-sm text-gray-500">{contact.company}</span>}
                  </div>
                </div>
                {!editing && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => startEdit(contact)}>
                      <Edit2 className="h-4 w-4" />
                      Edit
                    </Button>
                    <Button variant="danger-outline" size="sm" onClick={handleDelete}>
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {error && <Alert variant="error" className="mb-4">{error}</Alert>}

              {editing ? (
                <form onSubmit={handleSave} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <Label>Name</Label>
                      <Input value={editName} onChange={(e) => setEditName(e.target.value)} required />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Email</Label>
                      <Input type="email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} required />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Company</Label>
                      <Input value={editCompany} onChange={(e) => setEditCompany(e.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Title</Label>
                      <Input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Phone</Label>
                      <Input type="tel" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Stage</Label>
                      <Select value={editStage} onChange={(e) => setEditStage(e.target.value)}>
                        {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label>Notes</Label>
                    <Textarea value={editNotes} onChange={(e) => setEditNotes(e.target.value)} rows={3} />
                  </div>
                  <div className="flex gap-3">
                    <Button type="submit" disabled={saving}>{saving ? "Saving…" : "Save Changes"}</Button>
                    <Button type="button" variant="secondary" onClick={() => setEditing(false)}>Cancel</Button>
                  </div>
                </form>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <a href={`mailto:${contact.email}`} className="text-brand hover:underline">{contact.email}</a>
                  </div>
                  {contact.phone && (
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-700">{contact.phone}</span>
                    </div>
                  )}
                  {contact.title && (
                    <div className="flex items-center gap-2 text-sm">
                      <Briefcase className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-700">{contact.title}</span>
                    </div>
                  )}
                  {contact.company && (
                    <div className="flex items-center gap-2 text-sm">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-700">{contact.company}</span>
                    </div>
                  )}
                  {contact.notes && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <p className="text-xs text-gray-500 mb-1">Notes</p>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{contact.notes}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Meeting history */}
        <div>
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CalendarDays className="h-4 w-4 text-gray-400" />
                <CardTitle>Meetings ({meetings.length})</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {meetings.length === 0 ? (
                <p className="text-sm text-gray-400">No meetings yet.</p>
              ) : (
                <ul className="space-y-2">
                  {meetings.map((m) => (
                    <li key={m.id} className="border-b border-gray-100 pb-2 last:border-0">
                      <Link href={`/meetings/${m.id}`} className="text-sm font-medium text-gray-900 hover:text-brand">
                        {m.title}
                      </Link>
                      <p className="text-xs text-gray-500 mt-0.5">{m.start}</p>
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
