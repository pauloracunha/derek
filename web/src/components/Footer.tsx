// Texto explicativo (FR-008) + atribuição de licença das fontes (FR-016), sempre visível.
export default function Footer() {
  return (
    <div className="footer">
      <p>
        Um mesmo lugar pode aparecer com múltiplos pontos no mapa quando há mais de uma
        hipótese plausível para sua localização real — o Atlas de Atos preserva essa
        incerteza em vez de escolher um único ponto arbitrário.
      </p>
      <p className="footer__attribution">
        Dados de geolocalização: <a href="https://github.com/openbibleinfo/Bible-Geocoding-Data" target="_blank" rel="noreferrer">OpenBible.info Bible Geocoding Data</a> (CC BY 4.0).{' '}
        Referências cruzadas: <a href="https://www.openbible.info/labs/cross-references/" target="_blank" rel="noreferrer">OpenBible.info Cross References</a> (CC BY).
      </p>
    </div>
  )
}
