"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CalendarDays, Users2, CheckCircle, Clock, Plus, ArrowRight } from "lucide-react";
import { fetchMeetings, fetchContacts, fetchTeam, type MeetingRow } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageSpinner } from "@/components/ui/spinner";

interface Stats {
  upcomingCount: number;
  thisWeekCount: number;
  contactsCount: number;
  teamSize: number;
  completedCount: number;
}

function statusBadge(status: string) {
  if (status === "completed") return <Badge variant="success">Completed</Badge>;
  if (status === "cancelled") return <Badge variant="danger">Cancelled</Badge>;
  return <Badge variant="info">Scheduled</Badge>;
}

export default function DashboardPage() {
  const [meetings, setMeetings] = useState<MeetingRow[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const now = new Date().toISOString();
    const weekEnd = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

    Promise.all([
      fetchMeetings({ limit: 5, offset: 0 }),
      fetchMeetings({ start_after: now, limit: 100 }),
      fetchMeetings({ start_after: now, start_before: weekEnd, limit: 100 }),
      fetchContacts(),
      fetchTeam(),
      fetchMeetings({ status: "completed", limit: 100 }),
    ]).then(([recent, upcoming, thisWeek, contacts, team, completed]) => {
      setMeetings(recent);
      setStats({
        upcomingCount: upcoming.length,
        thisWeekCount: thisWeek.length,
        contactsCount: contacts.length,
        teamSize: team.members.length,
        completedCount: completed.length,
      });
    }).catch(() => null).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <AppShell title="Dashboard">
      <PageSpinner />
    </AppShell>
  );

  return (
    <AppShell
      title="Dashboard"
      actions={
        <Link href="/schedule">
          <Button size="sm">
            <Plus className="h-4 w-4" />
            Schedule Meeting
          </Button>
        </Link>
      }
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
                <CalendarDays className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats?.upcomingCount ?? 0}</p>
                <p className="text-xs text-gray-500 mt-0.5">Upcoming</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats?.thisWeekCount ?? 0}</p>
                <p className="text-xs text-gray-500 mt-0.5">This Week</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50">
                <Users2 className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats?.contactsCount ?? 0}</p>
                <p className="text-xs text-gray-500 mt-0.5">Contacts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
                <Clock className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats?.completedCount ?? 0}</p>
                <p className="text-xs text-gray-500 mt-0.5">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Meetings + Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Activity</CardTitle>
                <Link href="/meetings" className="text-xs text-brand hover:underline flex items-center gap-1">
                  View all <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="schedulr-table">
                <thead>
                  <tr>
                    <th>Meeting</th>
                    <th>Host</th>
                    <th>Start</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {meetings.length === 0 && (
                    <tr>
                      <td colSpan={4} className="text-center py-8 text-gray-400 text-sm">
                        No meetings yet
                      </td>
                    </tr>
                  )}
                  {meetings.map((m) => (
                    <tr key={m.id}>
                      <td>
                        <Link href={`/meetings/${m.id}`} className="font-medium text-gray-900 hover:text-brand">
                          {m.title}
                        </Link>
                      </td>
                      <td className="text-gray-600">{m.host}</td>
                      <td className="text-gray-600 text-xs">{m.start}</td>
                      <td>{statusBadge(m.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-3">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href="/schedule" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <CalendarDays className="h-4 w-4" />
                  Book a Meeting
                </Button>
              </Link>
              <Link href="/contacts" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <Users2 className="h-4 w-4" />
                  Add Contact
                </Button>
              </Link>
              <Link href="/availability" className="block">
                <Button variant="outline" className="w-full justify-start">
                  <Clock className="h-4 w-4" />
                  Set Availability
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Team</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-gray-900">{stats?.teamSize ?? 0}</p>
              <p className="text-sm text-gray-500 mt-1">Active members</p>
              <Link href="/team" className="text-xs text-brand hover:underline flex items-center gap-1 mt-2">
                Manage team <ArrowRight className="h-3 w-3" />
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
