import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "../error-boundary";

// エラーを投げるコンポーネント
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error("Test error");
  }
  return <div>No error</div>;
};

describe("ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("No error")).toBeInTheDocument();
  });

  it("renders error UI when there is an error", () => {
    // コンソールエラーを抑制
    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
    expect(
      screen.getByText("申し訳ございません。予期しないエラーが発生しました。"),
    ).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("shows retry and reload buttons", () => {
    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("再試行")).toBeInTheDocument();
    expect(screen.getByText("ページを再読み込み")).toBeInTheDocument();
    expect(screen.getByText("ホームに戻る")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("shows error details in development mode", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("エラー詳細:")).toBeInTheDocument();
    expect(screen.getByText("Test error")).toBeInTheDocument();

    consoleSpy.mockRestore();
    process.env.NODE_ENV = originalEnv;
  });
});
