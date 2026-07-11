"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Search, Users2 } from "lucide-react";
import { fetchContacts, createContact, type ContactOut } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { PageSpinner } from "@/components/ui/spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Alert } from "@/components/ui/alert";

const STAGES = ["lead", "prospect", "opportunity", "customer", "churned"];

function stageBadge(stage: string) {
  const map: Record<string, "default" | "info" | "warning" | "success" | "danger"> = {
    lead: "default",
    prospect: "info",
    opportunity: "warning",
    customer: "success",
    churned: "danger",
  };
  return <Badge variant={map[stage] ?? "default"}>{stage}</Badge>;
}

export default function ContactsPage() {
  const [contacts, setContacts] = useState<ContactOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [stageFilter, setStageFilter] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);

  // New contact form
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newCompany, setNewCompany] = useState("");
  const [newStage, setNewStage] = useState("lead");
  const [formError, setFormError] = useState<string | null>(null);

  function load() {
    fetchContacts()
      .then(setContacts)
      .catch(() => setError("Could not load contacts"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  const filtered = contacts.filter((c) => {
    const matchSearch = !search
      || c.name.toLowerCase().includes(search.toLowerCase())
      || c.email.toLowerCase().includes(search.toLowerCase())
      || (c.company?.toLowerCase().includes(search.toLowerCase()) ?? false);
    const matchStage = !stageFilter || c.stage === stageFilter;
    return matchSearch && matchStage;
  });

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!newName || !newEmail) {
      setFormError("Name and email are required.");
      return;
    }
    setSaving(true);
    try {
      await createContact({ name: newName, email: newEmail, company: newCompany || undefined, stage: newStage });
      setShowAdd(false);
      setNewName(""); setNewEmail(""); setNewCompany(""); setNewStage("lead");
      load();
    } catch {
      setFormError("Failed to create contact.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell
      title="Contacts"
      actions={
        <Button size="sm" onClick={() => setShowAdd(true)}>
          <Plus className="h-4 w-4" />
          Add Contact
        </Button>
      }
    >
      {/* Add Contact Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <Card className="w-full max-w-md shadow-xl">
            <CardHeader>
              <CardTitle>New Contact</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                {formError && <Alert variant="error">{formError}</Alert>}
                <div className="space-y-1.5">
                  <Label>Name *</Label>
                  <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Full name" required />
                </div>
                <div className="space-y-1.5">
                  <Label>Email *</Label>
                  <Input type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="email@company.com" required />
                </div>
                <div className="space-y-1.5">
                  <Label>Company</Label>
                  <Input value={newCompany} onChange={(e) => setNewCompany(e.target.value)} placeholder="Acme Corp" />
                </div>
                <div className="space-y-1.5">
                  <Label>Stage</Label>
                  <Select value={newStage} onChange={(e) => setNewStage(e.target.value)}>
                    {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </Select>
                </div>
                <div className="flex gap-3 pt-2">
                  <Button type="submit" disabled={saving}>{saving ? "Creating…" : "Create Contact"}</Button>
                  <Button type="button" variant="secondary" onClick={() => setShowAdd(false)}>Cancel</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-4">
        <div className="p-4 flex gap-3 items-center">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              className="pl-8"
              placeholder="Search contacts…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Select value={stageFilter} onChange={(e) => setStageFilter(e.target.value)} className="w-36">
            <option value="">All stages</option>
            {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
          </Select>
        </div>
      </Card>

      {/* List */}
      <Card>
        {loading ? (
          <PageSpinner />
        ) : error ? (
          <div className="p-6 text-red-600 text-sm">{error}</div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={Users2}
            title="No contacts found"
            description="Add your first contact to get started."
            action={<Button size="sm" onClick={() => setShowAdd(true)}><Plus className="h-4 w-4" />Add Contact</Button>}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="schedulr-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Company</th>
                  <th>Email</th>
                  <th>Stage</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={c.id}>
                    <td className="font-medium">
                      <Link href={`/contacts/${c.id}`} className="hover:text-brand">{c.name}</Link>
                    </td>
                    <td className="text-gray-600">{c.company ?? "—"}</td>
                    <td className="text-gray-500 text-sm">{c.email}</td>
                    <td>{stageBadge(c.stage)}</td>
                    <td>
                      <Link href={`/contacts/${c.id}`}>
                        <Button variant="ghost" size="sm">View</Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
