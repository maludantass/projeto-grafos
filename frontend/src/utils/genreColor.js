const PALETTE = [
  '#00e676','#d500f9','#2979ff','#ff2d78','#ffea00','#00b0ff',
  '#ff6d00','#76ff03','#e040fb','#00e5ff','#ff4081','#69f0ae',
  '#40c4ff','#ffd740','#ff6e40',
]

export function genreColor(genre = '') {
  let h = 0
  for (let i = 0; i < genre.length; i++) h = (h * 31 + genre.charCodeAt(i)) & 0xffff
  return PALETTE[h % PALETTE.length]
}
