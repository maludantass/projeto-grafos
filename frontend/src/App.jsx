import { useState } from 'react'
import SidebarLeft from './components/SidebarLeft'
import SidebarRight from './components/SidebarRight'
import Landing from './pages/Landing'
import Explore from './pages/Explore'

export default function App() {
  const [page, setPage]             = useState('landing')
  const [selectedNode, setSelectedNode] = useState(null)
  const [activeGenre, setActiveGenre]   = useState(null)
  const [strength, setStrength]         = useState(20)
  const [pathMode, setPathMode]         = useState(false)

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
        marginLeft: 200,
        marginRight: page === 'explore' ? 280 : 0,
        transition: 'margin-right .3s ease',
      }}>
        {page === 'landing'
          ? <Landing setPage={setPage} />
          : <Explore
              activeGenre={activeGenre}
              strength={strength}
              selectedNode={selectedNode}
              setSelectedNode={setSelectedNode}
              pathMode={pathMode}
              setPathMode={setPathMode}
            />
        }
      </main>

      {page === 'explore' && (
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
