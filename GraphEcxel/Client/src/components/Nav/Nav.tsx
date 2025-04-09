import './nav.scss'

interface INavProps {
   isActive: string
}

interface INavLinks {
   id: number,
   href: string,
   className_li: string,
   title: string,
   activestatus: string
}

function Nav(props: INavProps) {
   const NavLinks: INavLinks[] = [
      {id: 1, href: "/",  className_li: "", title: "Разметки инструкций", activestatus: "instractionMark"},
      {id: 2, href: "/instructionsfiles",  className_li: "", title: "Инструкции", activestatus: "instructionsfiles"},
      {id: 3, href: "/add_drug",  className_li: "", title: "Добавить лекарственные средства", activestatus: "addDrug"},
   ]
   
   return ( // bg-light
      <nav className="flex-column flex-shrink-0 p-3 sticky-top" style={{ width: '250px'}}> 
         <a href="/" className="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-decoration-none">
            <h1 className="fs-4">РНФ</h1>
         </a>
         <hr />

         <ul className="nav nav-pills flex-column mb-auto">
            {Array.isArray(NavLinks) && NavLinks.map(link=>
               <li className={`${link.className_li} nav-item`} key={link.id}>
                  <a href={link.href} className={ (props.isActive == link.activestatus) ? "nav-link active" : "nav-link link-dark"}>
                     {link.title}
                  </a>
               </li>
            )}

            <hr />
            <div>
               <a href="#" className="nav-link link-dark">
                  Настройки
               </a>
            </div>
         </ul>
    </nav>
    )
  }
  
  export default Nav