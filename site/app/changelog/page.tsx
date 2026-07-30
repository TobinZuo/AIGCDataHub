import type { Metadata } from "next";
import changelog from "../changelog-data.json";
import { ChangelogView } from "./changelog-view";

export const metadata: Metadata = {
  title: "变更记录 | AIGCDataHub",
  description: "从模型、数据集、数据关系、排行榜、监控和未披露六个维度了解 AIGCDataHub 的每次更新。",
  alternates: { canonical: "https://tobinzuo.github.io/AIGCDataHub/changelog/" },
};

export default function ChangelogPage() {
  return <ChangelogView changelog={changelog} />;
}
