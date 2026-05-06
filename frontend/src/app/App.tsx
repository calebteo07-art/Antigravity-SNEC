import { RouterProvider } from "react-router";
import { AnimatePresence } from "motion/react";
import { router } from "./routes";

export default function App() {
  return (
    <AnimatePresence mode="wait">
      <RouterProvider router={router} />
    </AnimatePresence>
  );
}
