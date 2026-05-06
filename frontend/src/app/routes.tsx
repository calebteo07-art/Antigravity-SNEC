import { createBrowserRouter } from "react-router";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { ChatScreen } from "./components/ChatScreen";
import { FlashcardScreen } from "./components/FlashcardScreen";
import { SummaryScreen } from "./components/SummaryScreen";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: OnboardingScreen,
  },
  {
    path: "/chat",
    Component: ChatScreen,
  },
  {
    path: "/flashcards",
    Component: FlashcardScreen,
  },
  {
    path: "/summary",
    Component: SummaryScreen,
  },
]);
