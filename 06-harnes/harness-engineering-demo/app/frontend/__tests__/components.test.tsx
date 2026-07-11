/**
 * Vitest component tests for Schedulr UI components.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

// Mock Next.js router
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/",
  useParams: () => ({}),
}));

// Mock Next.js Link
vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  ),
}));

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Spinner, PageSpinner } from "@/components/ui/spinner";
import { Select } from "@/components/ui/select";

// ── Button ────────────────────────────────────────────────────────────────────

describe("Button", () => {
  it("renders with default variant", () => {
    render(<Button>Click me</Button>);
    const btn = screen.getByRole("button", { name: "Click me" });
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveClass("bg-brand");
  });

  it("renders secondary variant", () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByRole("button", { name: "Secondary" });
    expect(btn).toHaveClass("bg-gray-100");
  });

  it("renders outline variant", () => {
    render(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole("button")).toHaveClass("border");
  });

  it("renders danger variant", () => {
    render(<Button variant="danger">Delete</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-red-500");
  });

  it("is disabled when disabled prop set", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("fires onClick when clicked", () => {
    const handler = vi.fn();
    render(<Button onClick={handler}>Click</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(handler).toHaveBeenCalledOnce();
  });

  it("does not fire onClick when disabled", () => {
    const handler = vi.fn();
    render(<Button disabled onClick={handler}>Click</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(handler).not.toHaveBeenCalled();
  });

  it("renders small size", () => {
    render(<Button size="sm">Small</Button>);
    expect(screen.getByRole("button")).toHaveClass("h-8");
  });
});

// ── Badge ─────────────────────────────────────────────────────────────────────

describe("Badge", () => {
  it("renders default badge", () => {
    render(<Badge>Lead</Badge>);
    expect(screen.getByText("Lead")).toBeInTheDocument();
    expect(screen.getByText("Lead")).toHaveClass("bg-gray-100");
  });

  it("renders success badge", () => {
    render(<Badge variant="success">Active</Badge>);
    expect(screen.getByText("Active")).toHaveClass("bg-green-100");
  });

  it("renders danger badge", () => {
    render(<Badge variant="danger">Cancelled</Badge>);
    expect(screen.getByText("Cancelled")).toHaveClass("bg-red-100");
  });

  it("renders info badge", () => {
    render(<Badge variant="info">Scheduled</Badge>);
    expect(screen.getByText("Scheduled")).toHaveClass("bg-blue-100");
  });
});

// ── Input ─────────────────────────────────────────────────────────────────────

describe("Input", () => {
  it("renders an input element", () => {
    render(<Input placeholder="Search" />);
    expect(screen.getByPlaceholderText("Search")).toBeInTheDocument();
  });

  it("is disabled when disabled prop set", () => {
    render(<Input disabled />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("calls onChange when typed", () => {
    const handler = vi.fn();
    render(<Input onChange={handler} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "hello" } });
    expect(handler).toHaveBeenCalled();
  });
});

// ── Alert ─────────────────────────────────────────────────────────────────────

describe("Alert", () => {
  it("renders error alert", () => {
    const { container } = render(<Alert variant="error">Something went wrong</Alert>);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(container.firstChild).toHaveClass("bg-red-50");
  });

  it("renders success alert", () => {
    const { container } = render(<Alert variant="success">Saved!</Alert>);
    expect(screen.getByText("Saved!")).toBeInTheDocument();
    expect(container.firstChild).toHaveClass("bg-green-50");
  });

  it("renders warning alert", () => {
    const { container } = render(<Alert variant="warning">Warning</Alert>);
    expect(screen.getByText("Warning")).toBeInTheDocument();
    expect(container.firstChild).toHaveClass("bg-amber-50");
  });
});

// ── Card ──────────────────────────────────────────────────────────────────────

describe("Card", () => {
  it("renders card with title and content", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
        </CardHeader>
        <CardContent>Content here</CardContent>
      </Card>
    );
    expect(screen.getByText("Test Card")).toBeInTheDocument();
    expect(screen.getByText("Content here")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<Card className="my-custom-class">Content</Card>);
    expect(container.firstChild).toHaveClass("my-custom-class");
  });
});

// ── EmptyState ────────────────────────────────────────────────────────────────

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(
      <EmptyState
        title="No meetings"
        description="Schedule your first meeting to get started."
      />
    );
    expect(screen.getByText("No meetings")).toBeInTheDocument();
    expect(screen.getByText("Schedule your first meeting to get started.")).toBeInTheDocument();
  });

  it("renders action when provided", () => {
    render(
      <EmptyState
        title="Empty"
        action={<Button>Add Item</Button>}
      />
    );
    expect(screen.getByRole("button", { name: "Add Item" })).toBeInTheDocument();
  });
});

// ── Spinner ───────────────────────────────────────────────────────────────────

describe("Spinner", () => {
  it("renders spinner element", () => {
    const { container } = render(<Spinner />);
    expect(container.firstChild).toHaveClass("animate-spin");
  });

  it("renders PageSpinner", () => {
    const { container } = render(<PageSpinner />);
    expect(container.querySelector(".animate-spin")).toBeInTheDocument();
  });
});

// ── Select ────────────────────────────────────────────────────────────────────

describe("Select", () => {
  it("renders options", () => {
    render(
      <Select>
        <option value="a">Option A</option>
        <option value="b">Option B</option>
      </Select>
    );
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    expect(screen.getByText("Option A")).toBeInTheDocument();
  });

  it("calls onChange on selection", () => {
    const handler = vi.fn();
    render(
      <Select onChange={handler}>
        <option value="a">A</option>
        <option value="b">B</option>
      </Select>
    );
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "b" } });
    expect(handler).toHaveBeenCalled();
  });
});
