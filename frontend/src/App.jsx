import { useState } from 'react'
import SidebarLeft from './components/SidebarLeft'
import SidebarRight from './components/SidebarRight'
import Landing from './pages/Landing'
import Explore from './pages/Explore'
import Benchmark from './pages/Benchmark'
import Visualizacoes from './pages/Visualizacoes'
import Comparacao from './pages/Comparacao'
import Sobre from './pages/Sobre'

export default function App() {
  const [page, setPage]             = useState('landing')
  const [selectedNode, setSelectedNode] = useState(null)
  const [activeGenre, setActiveGenre]   = useState(null)
  const [strength, setStrength]         = useState(20)
  const [pathMode, setPathMode]         = useState(false)

  const showRightSidebar = page === 'explore'

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <SidebarLeft
        page={page}
        setPage={setPage}
        activeGenre={activeGenre}
        setActiveGenre={setActiveGenre}
      />

      <main style={{
        flex: 1,
        position: 'relative',
        overflow: 'hidden',
        marginLeft: 300,
        marginRight: showRightSidebar ? 280 : 0,
        transition: 'margin-right .3s ease',
      }}>
        {page === 'landing'    && <Landing setPage={setPage} />}
        {page === 'explore'    && (
          <Explore
            activeGenre={activeGenre}
            strength={strength}
            selectedNode={selectedNode}
            setSelectedNode={setSelectedNode}
            pathMode={pathMode}
            setPathMode={setPathMode}
          />
        )}
        {page === 'benchmark'  && <Benchmark />}
        {page === 'viz'        && <Visualizacoes />}
        {page === 'comparacao' && <Comparacao />}
        {page === 'sobre'      && <Sobre />}
      </main>

      {showRightSidebar && (
        <SidebarRight
          selectedNode={selectedNode}
          activeGenre={activeGenre}
          setActiveGenre={setActiveGenre}
          strength={strength}
          setStrength={setStrength}
          pathMode={pathMode}
          setPathMode={setPathMode}
        />
      )}
    </div>
  )
}