import catalog from "./catalog-data.json";
import { CatalogExplorer } from "./catalog-explorer";

export default function Home() {
  return <CatalogExplorer catalog={catalog} />;
}
