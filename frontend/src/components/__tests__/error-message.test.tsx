import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ErrorMessage } from "../error-message";

describe("ErrorMessage", () => {
  it("renders error message with default title", () => {
    render(<ErrorMessage message="Test error message" />);

    expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
    expect(screen.getByText("Test error message")).toBeInTheDocument();
  });

  it("renders with custom title", () => {
    render(<ErrorMessage title="Custom Error" message="Test error message" />);

    expect(screen.getByText("Custom Error")).toBeInTheDocument();
    expect(screen.getByText("Test error message")).toBeInTheDocument();
  });

  it("shows retry button when onRetry is provided", async () => {
    const handleRetry = jest.fn();
    const user = userEvent.setup();

    render(<ErrorMessage message="Test error" onRetry={handleRetry} />);

    const retryButton = screen.getByText("再試行");
    expect(retryButton).toBeInTheDocument();

    await user.click(retryButton);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it("shows dismiss button when onDismiss is provided", async () => {
    const handleDismiss = jest.fn();
    const user = userEvent.setup();

    render(<ErrorMessage message="Test error" onDismiss={handleDismiss} />);

    const dismissButton = screen.getByText("閉じる");
    expect(dismissButton).toBeInTheDocument();

    await user.click(dismissButton);
    expect(handleDismiss).toHaveBeenCalledTimes(1);
  });

  it("shows details when showDetails is true", () => {
    render(<ErrorMessage message="Test error" showDetails={true} details="Error stack trace" />);

    expect(screen.getByText("詳細を表示")).toBeInTheDocument();
  });

  it("applies correct variant styles", () => {
    const { rerender } = render(<ErrorMessage message="Test error" variant="destructive" />);

    const card = screen.getByText("Test error").closest(".border-red-200");
    expect(card).toBeInTheDocument();

    rerender(<ErrorMessage message="Test error" variant="warning" />);
    const warningCard = screen.getByText("Test error").closest(".border-yellow-200");
    expect(warningCard).toBeInTheDocument();
  });
});
