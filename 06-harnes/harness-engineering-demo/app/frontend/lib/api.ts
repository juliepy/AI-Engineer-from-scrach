// Tiny API client. Smell: hardcoded base URL fallback, mixed camelCase/snake_case.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("schedulr_token");
}

export function setToken(t: string) {
  window.localStorage.setItem("schedulr_token", t);
}

export function clearToken() {
  window.localStorage.removeItem("schedulr_token");
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function legacyHeaders(): Record<string, string> {
  const tok = window.localStorage.getItem("schedulr_session_token");
  return tok ? { "X-Session-Token": tok } : {};
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init.headers as Record<string, string> | undefined),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw Object.assign(new Error(body || res.statusText), { status: res.status });
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

async function legacyFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...legacyHeaders(),
      ...(init.headers as Record<string, string> | undefined),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw Object.assign(new Error(body || res.statusText), { status: res.status });
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  // Also do a legacy login so contacts routes work
  const legacyRes = await fetch(`${API_BASE}/api/auth/legacy-login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (legacyRes.ok) {
    const legacyData = await legacyRes.json();
    window.localStorage.setItem("schedulr_session_token", legacyData.session_token);
  }
  return data.access_token;
}

export interface UserOut {
  id: number;
  email: string;
  full_name: string;
  timezone: string;
  role: string;
  team_id: number;
}

export async function getMe(): Promise<UserOut> {
  return apiFetch<UserOut>("/api/auth/me");
}

export async function updateProfile(data: { full_name?: string; timezone?: string }): Promise<UserOut> {
  return apiFetch<UserOut>("/api/auth/me/profile", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function changePassword(current_password: string, new_password: string): Promise<void> {
  return apiFetch("/api/auth/me/change-password", {
    method: "POST",
    body: JSON.stringify({ current_password, new_password }),
  });
}

// ── Meetings ──────────────────────────────────────────────────────────────────

export interface InviteeOut {
  id: number;
  contact_id: number;
  contact_name: string;
  contact_email: string;
  response: string;
}

export interface MeetingRow {
  id: number;
  title: string;
  host: string | null;
  host_id: number;
  start: string;
  end: string;
  timezone: string;
  status: string;
  notes: string | null;
  inviteeCount: number;
  invitees: InviteeOut[];
}

export interface MeetingFilters {
  host_id?: number;
  start_after?: string;
  start_before?: string;
  contact_id?: number;
  status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export async function fetchMeetings(filters: MeetingFilters = {}): Promise<MeetingRow[]> {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== "" && v !== null) params.set(k, String(v));
  }
  const qs = params.toString();
  return apiFetch<MeetingRow[]>(`/api/meetings${qs ? "?" + qs : ""}`);
}

export async function getMeeting(id: number): Promise<MeetingRow> {
  return apiFetch<MeetingRow>(`/api/meetings/${id}`);
}

export async function createMeeting(data: {
  title: string;
  start_time: string;
  end_time: string;
  meeting_timezone: string;
  notes?: string;
  invitee_contact_ids?: number[];
}): Promise<MeetingRow> {
  return apiFetch<MeetingRow>("/api/meetings", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMeeting(id: number, data: Partial<{
  title: string;
  notes: string;
  start_time: string;
  end_time: string;
  meeting_timezone: string;
  status: string;
}>): Promise<MeetingRow> {
  return apiFetch<MeetingRow>(`/api/meetings/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function cancelMeeting(id: number): Promise<void> {
  return apiFetch(`/api/meetings/${id}`, { method: "DELETE" });
}

export async function updateRSVP(meetingId: number, inviteeId: number, response: string): Promise<void> {
  return apiFetch(`/api/meetings/${meetingId}/invitees/${inviteeId}/rsvp`, {
    method: "PATCH",
    body: JSON.stringify({ response }),
  });
}

// Only PDF export exists today. SCH-142 adds CSV (the workshop builds it live).
export function exportUrl(format: string): string {
  const token = getToken();
  return `${API_BASE}/api/meetings/export?format=${format}&token=${token}`;
}

// ── Contacts ──────────────────────────────────────────────────────────────────

export interface ContactOut {
  id: number;
  name: string;
  email: string;
  company: string | null;
  phone: string | null;
  title: string | null;
  notes: string | null;
  stage: string;
  created_at: string;
}

export async function fetchContacts(): Promise<ContactOut[]> {
  return legacyFetch<ContactOut[]>("/api/contacts");
}

export async function getContact(id: number): Promise<ContactOut> {
  return legacyFetch<ContactOut>(`/api/contacts/${id}`);
}

export async function createContact(data: Partial<ContactOut>): Promise<ContactOut> {
  return legacyFetch<ContactOut>("/api/contacts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateContact(id: number, data: Partial<ContactOut>): Promise<ContactOut> {
  return legacyFetch<ContactOut>(`/api/contacts/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteContact(id: number): Promise<void> {
  return legacyFetch(`/api/contacts/${id}`, { method: "DELETE" });
}

// ── Availability ──────────────────────────────────────────────────────────────

export interface AvailabilitySlot {
  id: number;
  user_id: number;
  weekday: number;
  start: string;
  end: string;
}

export async function fetchAvailability(): Promise<AvailabilitySlot[]> {
  return apiFetch<AvailabilitySlot[]>("/api/availability");
}

export async function setAvailability(slots: { weekday: number; start: string; end: string }[]): Promise<AvailabilitySlot[]> {
  return apiFetch<AvailabilitySlot[]>("/api/availability", {
    method: "PUT",
    body: JSON.stringify({ slots }),
  });
}

// ── Teams ─────────────────────────────────────────────────────────────────────

export interface TeamMember {
  id: number;
  name: string;
  email: string;
  timezone: string;
  role: string;
}

export interface TeamOut {
  id: number;
  name: string;
  slug: string;
  members: TeamMember[];
}

export async function fetchTeam(): Promise<TeamOut> {
  return apiFetch<TeamOut>("/api/teams/me");
}

export async function inviteMember(data: {
  email: string;
  full_name: string;
  role?: string;
  timezone?: string;
}): Promise<TeamMember> {
  return apiFetch<TeamMember>("/api/teams/me/members", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMemberRole(userId: number, role: string): Promise<TeamMember> {
  return apiFetch<TeamMember>(`/api/teams/me/members/${userId}/role`, {
    method: "PATCH",
    body: JSON.stringify({ role }),
  });
}

export async function removeMember(userId: number): Promise<void> {
  return apiFetch(`/api/teams/me/members/${userId}`, { method: "DELETE" });
}
