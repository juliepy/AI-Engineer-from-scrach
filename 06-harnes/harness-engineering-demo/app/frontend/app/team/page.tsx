"use client";

import { useEffect, useState } from "react";
import { Users, Plus, Globe, Shield, UserMinus, ChevronDown } from "lucide-react";
import {
  fetchTeam,
  inviteMember,
  updateMemberRole,
  removeMember,
  getMe,
  type TeamOut,
  type TeamMember,
  type UserOut,
} from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { PageSpinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";

export default function TeamPage() {
  const [team, setTeam] = useState<TeamOut | null>(null);
  const [me, setMe] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInvite, setShowInvite] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Invite form
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteName, setInviteName] = useState("");
  const [inviteRole, setInviteRole] = useState("member");
  const [inviteTz, setInviteTz] = useState("UTC");

  function load() {
    Promise.all([fetchTeam(), getMe()])
      .then(([t, u]) => { setTeam(t); setMe(u); })
      .catch(() => setError("Could not load team"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSaving(true);
    try {
      await inviteMember({ email: inviteEmail, full_name: inviteName, role: inviteRole, timezone: inviteTz });
      setShowInvite(false);
      setInviteEmail(""); setInviteName(""); setInviteRole("member"); setInviteTz("UTC");
      load();
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message ?? "Failed to invite member";
      setFormError(msg.includes("409") ? "Email already in use" : msg);
    } finally {
      setSaving(false);
    }
  }

  async function handleRoleChange(userId: number, role: string) {
    try {
      await updateMemberRole(userId, role);
      load();
    } catch {
      setError("Failed to update role");
    }
  }

  async function handleRemove(userId: number, name: string) {
    if (!confirm(`Remove ${name} from the team?`)) return;
    try {
      await removeMember(userId);
      load();
    } catch {
      setError("Failed to remove member");
    }
  }

  if (loading) return <AppShell title="Team"><PageSpinner /></AppShell>;

  const isAdmin = me?.role === "admin";

  return (
    <AppShell
      title="Team"
      actions={isAdmin ? (
        <Button size="sm" onClick={() => setShowInvite(true)}>
          <Plus className="h-4 w-4" />
          Invite Member
        </Button>
      ) : undefined}
    >
      {error && <Alert variant="error" className="mb-4">{error}</Alert>}

      {/* Invite modal */}
      {showInvite && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <Card className="w-full max-w-md shadow-xl">
            <CardHeader>
              <CardTitle>Invite Team Member</CardTitle>
              <CardDescription>A temporary password <code className="text-xs">changeme123</code> will be set.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleInvite} className="space-y-4">
                {formError && <Alert variant="error">{formError}</Alert>}
                <div className="space-y-1.5">
                  <Label>Full Name</Label>
                  <Input value={inviteName} onChange={(e) => setInviteName(e.target.value)} placeholder="Alex Smith" required />
                </div>
                <div className="space-y-1.5">
                  <Label>Email</Label>
                  <Input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="alex@company.com" required />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>Role</Label>
                    <Select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)}>
                      <option value="member">Member</option>
                      <option value="admin">Admin</option>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <Label>Timezone</Label>
                    <Input value={inviteTz} onChange={(e) => setInviteTz(e.target.value)} placeholder="UTC" />
                  </div>
                </div>
                <div className="flex gap-3 pt-2">
                  <Button type="submit" disabled={saving}>{saving ? "Inviting…" : "Send Invite"}</Button>
                  <Button type="button" variant="secondary" onClick={() => setShowInvite(false)}>Cancel</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-brand" />
            <CardTitle>{team?.name}</CardTitle>
            <Badge variant="default" className="ml-2">{team?.members.length} members</Badge>
          </div>
          <CardDescription>Slug: <code className="text-xs">{team?.slug}</code></CardDescription>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="schedulr-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Timezone</th>
                <th>Role</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {team?.members.map((m) => (
                <tr key={m.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-50 text-brand text-xs font-semibold">
                        {m.name.charAt(0)}
                      </div>
                      <span className="font-medium text-gray-900">{m.name}</span>
                      {m.id === me?.id && <Badge variant="brand" className="text-xs">You</Badge>}
                    </div>
                  </td>
                  <td className="text-gray-500 text-sm">{m.email}</td>
                  <td>
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <Globe className="h-3.5 w-3.5 text-gray-400" />
                      {m.timezone}
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1">
                      {m.role === "admin" && <Shield className="h-3.5 w-3.5 text-brand" />}
                      <span className="text-sm capitalize text-gray-700">{m.role}</span>
                    </div>
                  </td>
                  {isAdmin && (
                    <td>
                      {m.id !== me?.id && (
                        <div className="flex gap-2">
                          <Select
                            value={m.role}
                            onChange={(e) => handleRoleChange(m.id, e.target.value)}
                            className="w-28 h-7 text-xs"
                          >
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                          </Select>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemove(m.id, m.name)}
                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            <UserMinus className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </AppShell>
  );
}
