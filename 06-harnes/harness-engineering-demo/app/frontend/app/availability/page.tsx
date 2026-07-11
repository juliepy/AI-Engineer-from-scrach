"use client";

import { useEffect, useState } from "react";
import { Clock, Save } from "lucide-react";
import { fetchAvailability, setAvailability, type AvailabilitySlot } from "@/lib/api";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { PageSpinner } from "@/components/ui/spinner";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

interface SlotEdit {
  weekday: number;
  enabled: boolean;
  start: string;
  end: string;
}

function buildDefault(): SlotEdit[] {
  return DAYS.map((_, i) => ({
    weekday: i,
    enabled: i < 5, // Mon-Fri enabled by default
    start: "09:00",
    end: "17:00",
  }));
}

export default function AvailabilityPage() {
  const [slots, setSlots] = useState<SlotEdit[]>(buildDefault());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAvailability().then((existing: AvailabilitySlot[]) => {
      if (existing.length > 0) {
        setSlots(
          DAYS.map((_, i) => {
            const match = existing.find((s) => s.weekday === i);
            return {
              weekday: i,
              enabled: !!match,
              start: match?.start ?? "09:00",
              end: match?.end ?? "17:00",
            };
          })
        );
      }
    }).catch(() => null).finally(() => setLoading(false));
  }, []);

  function update(weekday: number, field: keyof SlotEdit, value: string | boolean) {
    setSlots((prev) => prev.map((s) => s.weekday === weekday ? { ...s, [field]: value } : s));
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const toSave = slots
        .filter((s) => s.enabled)
        .map(({ weekday, start, end }) => ({ weekday, start, end }));
      await setAvailability(toSave);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch {
      setError("Failed to save availability.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return (
    <AppShell title="Availability">
      <PageSpinner />
    </AppShell>
  );

  return (
    <AppShell title="Availability">
      <div className="max-w-xl">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-brand" />
              <CardTitle>Weekly Availability</CardTitle>
            </div>
            <CardDescription>
              Set your working hours for each day of the week. Times are in your local timezone.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {error && <Alert variant="error">{error}</Alert>}
            {success && <Alert variant="success">Availability saved!</Alert>}

            {slots.map((slot) => (
              <div
                key={slot.weekday}
                className={`flex items-center gap-4 rounded-lg px-4 py-3 border transition-colors ${
                  slot.enabled ? "border-gray-200 bg-white" : "border-gray-100 bg-gray-50"
                }`}
              >
                <label className="flex items-center gap-2 w-28 shrink-0 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={slot.enabled}
                    onChange={(e) => update(slot.weekday, "enabled", e.target.checked)}
                    className="rounded accent-brand"
                  />
                  <span className={`text-sm font-medium ${slot.enabled ? "text-gray-900" : "text-gray-400"}`}>
                    {DAYS[slot.weekday]}
                  </span>
                </label>

                {slot.enabled ? (
                  <div className="flex items-center gap-2 flex-1">
                    <Input
                      type="time"
                      value={slot.start}
                      onChange={(e) => update(slot.weekday, "start", e.target.value)}
                      className="w-32"
                    />
                    <span className="text-gray-400 text-sm">to</span>
                    <Input
                      type="time"
                      value={slot.end}
                      onChange={(e) => update(slot.weekday, "end", e.target.value)}
                      className="w-32"
                    />
                  </div>
                ) : (
                  <span className="text-sm text-gray-400">Unavailable</span>
                )}
              </div>
            ))}

            <div className="pt-2">
              <Button onClick={handleSave} disabled={saving}>
                <Save className="h-4 w-4" />
                {saving ? "Saving…" : "Save Availability"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
