"use client";

import { useEffect, useState } from "react";
import { User, Lock, Bell, Puzzle } from "lucide-react";
import { getMe, updateProfile, changePassword, type UserOut } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { PageSpinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";

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

const CRM_INTEGRATIONS = [
  { name: "Salesforce", description: "Sync contacts and opportunities", status: "available" },
  { name: "HubSpot", description: "Two-way contact and deal sync", status: "available" },
  { name: "Pipedrive", description: "Deal pipeline integration", status: "coming_soon" },
];

export default function SettingsPage() {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  // Profile form
  const [fullName, setFullName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Password form
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwSaving, setPwSaving] = useState(false);
  const [pwMsg, setPwMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    getMe().then((u) => {
      setUser(u);
      setFullName(u.full_name);
      setTimezone(u.timezone);
    }).finally(() => setLoading(false));
  }, []);

  async function handleProfileSave(e: React.FormEvent) {
    e.preventDefault();
    setProfileSaving(true);
    setProfileMsg(null);
    try {
      const updated = await updateProfile({ full_name: fullName, timezone });
      setUser(updated);
      setProfileMsg({ type: "success", text: "Profile updated successfully." });
    } catch {
      setProfileMsg({ type: "error", text: "Failed to update profile." });
    } finally {
      setProfileSaving(false);
    }
  }

  async function handlePasswordChange(e: React.FormEvent) {
    e.preventDefault();
    setPwMsg(null);
    if (newPw !== confirmPw) {
      setPwMsg({ type: "error", text: "New passwords don't match." });
      return;
    }
    if (newPw.length < 8) {
      setPwMsg({ type: "error", text: "Password must be at least 8 characters." });
      return;
    }
    setPwSaving(true);
    try {
      await changePassword(currentPw, newPw);
      setPwMsg({ type: "success", text: "Password changed successfully." });
      setCurrentPw(""); setNewPw(""); setConfirmPw("");
    } catch {
      setPwMsg({ type: "error", text: "Incorrect current password." });
    } finally {
      setPwSaving(false);
    }
  }

  if (loading) return <AppShell title="Settings"><PageSpinner /></AppShell>;

  return (
    <AppShell title="Settings">
      <div className="max-w-2xl space-y-4">
        {/* Profile */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-brand" />
              <CardTitle>Profile</CardTitle>
            </div>
            <CardDescription>Update your display name and timezone.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileSave} className="space-y-4">
              {profileMsg && (
                <Alert variant={profileMsg.type}>{profileMsg.text}</Alert>
              )}
              <div className="space-y-1.5">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="email_ro">Email</Label>
                <Input id="email_ro" value={user?.email ?? ""} disabled className="bg-gray-50" />
                <p className="text-xs text-gray-400">Email cannot be changed here.</p>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="timezone">Timezone</Label>
                <Select
                  id="timezone"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                >
                  {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz}</option>)}
                </Select>
                <p className="text-xs text-gray-400">Meeting times are displayed in this timezone.</p>
              </div>
              <Button type="submit" disabled={profileSaving}>
                {profileSaving ? "Saving…" : "Save Profile"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Password */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-brand" />
              <CardTitle>Password</CardTitle>
            </div>
            <CardDescription>Change your account password.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {pwMsg && <Alert variant={pwMsg.type}>{pwMsg.text}</Alert>}
              <div className="space-y-1.5">
                <Label htmlFor="current_pw">Current Password</Label>
                <Input
                  id="current_pw"
                  type="password"
                  value={currentPw}
                  onChange={(e) => setCurrentPw(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="new_pw">New Password</Label>
                <Input
                  id="new_pw"
                  type="password"
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                  required
                  minLength={8}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="confirm_pw">Confirm New Password</Label>
                <Input
                  id="confirm_pw"
                  type="password"
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" disabled={pwSaving}>
                {pwSaving ? "Changing…" : "Change Password"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Notifications (stub) */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-brand" />
              <CardTitle>Notifications</CardTitle>
            </div>
            <CardDescription>Control when and how you receive notifications.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "Meeting reminders", description: "15 minutes before each meeting" },
              { label: "New meeting invites", description: "When someone adds you to a meeting" },
              { label: "Weekly digest", description: "Summary of your upcoming week" },
            ].map(({ label, description }) => (
              <label key={label} className="flex items-start justify-between gap-4 cursor-pointer">
                <div>
                  <p className="text-sm font-medium text-gray-900">{label}</p>
                  <p className="text-xs text-gray-500">{description}</p>
                </div>
                <input type="checkbox" defaultChecked className="mt-0.5 rounded accent-brand" />
              </label>
            ))}
          </CardContent>
        </Card>

        {/* Integrations (stub) */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Puzzle className="h-5 w-5 text-brand" />
              <CardTitle>CRM Integrations</CardTitle>
            </div>
            <CardDescription>Connect your CRM to sync contacts and deals.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {CRM_INTEGRATIONS.map(({ name, description, status }) => (
              <div key={name} className="flex items-center justify-between gap-4 py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{name}</p>
                  <p className="text-xs text-gray-500">{description}</p>
                </div>
                {status === "coming_soon" ? (
                  <Badge variant="default">Coming soon</Badge>
                ) : (
                  <Button variant="outline" size="sm">Connect</Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
