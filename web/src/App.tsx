import { useEffect, useState } from 'react'
import './App.css'
import { loadGraph, loadPlaces } from './services/dataLoader'
import { useAtlasStore } from './state/store'
import Map from './components/Map'
import PlaceDetail from './components/PlaceDetail'
import UnlocatablePanel from './components/UnlocatablePanel'
import ChapterTimeline from './components/ChapterTimeline'
import NetworkGraph from './components/NetworkGraph'
import Legend from './components/Legend'
import Footer from './components/Footer'

function App() {
  const setPlaces = useAtlasStore((s) => s.setPlaces)
  const setGraph = useAtlasStore((s) => s.setGraph)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([loadPlaces().then(setPlaces), loadGraph().then(setGraph)]).catch((e: Error) =>
      setError(e.message),
    )
  }, [setPlaces, setGraph])

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>Atlas de Atos</h1>
        <p className="app-subtitle">
          Rede de lugares do livro de Atos, preservando a incerteza de localização.
        </p>
      </header>

      {error && <div className="app-error">Erro ao carregar dados: {error}</div>}

      <main className="app-main">
        <section className="map-area" aria-label="Mapa">
          <Map />
        </section>

        <aside className="side-panel" aria-label="Painel lateral">
          <PlaceDetail />
          <UnlocatablePanel />
          <Legend />
        </aside>

        <section className="timeline-area" aria-label="Linha do tempo de capítulos">
          <ChapterTimeline />
        </section>

        <section className="graph-area" aria-label="Grafo de rede">
          <NetworkGraph />
        </section>
      </main>

      <footer className="app-footer">
        <Footer />
      </footer>
    </div>
  )
}

export default App
