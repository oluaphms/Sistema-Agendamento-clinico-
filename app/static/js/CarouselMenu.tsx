import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, X, Menu } from 'lucide-react';

interface MenuItem {
  id: string;
  name: string;
  icon: string;
  route: string;
  description?: string;
}

interface CarouselMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (route: string) => void;
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    icon: '📊',
    route: '/dashboard',
    description: 'Visão geral do sistema'
  },
  {
    id: 'agenda',
    name: 'Agenda',
    icon: '📅',
    route: '/agenda',
    description: 'Gerenciar agendamentos'
  },
  {
    id: 'pacientes',
    name: 'Pacientes',
    icon: '👥',
    route: '/pacientes',
    description: 'Cadastro de pacientes'
  },
  {
    id: 'profissionais',
    name: 'Profissionais',
    icon: '👨‍⚕️',
    route: '/profissionais',
    description: 'Equipe médica'
  },
  {
    id: 'relatorios',
    name: 'Relatórios',
    icon: '📈',
    route: '/relatorios',
    description: 'Análises e estatísticas'
  },
  {
    id: 'usuarios',
    name: 'Usuários',
    icon: '👤',
    route: '/usuarios',
    description: 'Gestão de usuários'
  },

  {
    id: 'configuracoes',
    name: 'Configurações',
    icon: '⚙️',
    route: '/configuracoes',
    description: 'Preferências do sistema'
  },
  {
    id: 'sobre',
    name: 'Sobre',
    icon: 'ℹ️',
    route: '/sobre',
    description: 'Informações do sistema'
  }
];

const CarouselMenu: React.FC<CarouselMenuProps> = ({ isOpen, onClose, onNavigate }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);
  const startX = useRef<number>(0);
  const currentX = useRef<number>(0);

  // Fecha o menu com ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev === 0 ? menuItems.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === menuItems.length - 1 ? 0 : prev + 1));
  };

  const handleItemClick = (item: MenuItem) => {
    onNavigate(item.route);
    onClose();
  };

  // Touch events para mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    startX.current = e.touches[0].clientX;
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    currentX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    
    const diff = startX.current - currentX.current;
    const threshold = 50;
    
    if (Math.abs(diff) > threshold) {
      if (diff > 0) {
        handleNext();
      } else {
        handlePrev();
      }
    }
    
    setIsDragging(false);
  };

  // Mouse drag events para desktop
  const handleMouseDown = (e: React.MouseEvent) => {
    startX.current = e.clientX;
    setIsDragging(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    currentX.current = e.clientX;
  };

  const handleMouseUp = () => {
    if (!isDragging) return;
    
    const diff = startX.current - currentX.current;
    const threshold = 50;
    
    if (Math.abs(diff) > threshold) {
      if (diff > 0) {
        handleNext();
      } else {
        handlePrev();
      }
    }
    
    setIsDragging(false);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          
          {/* Menu Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ 
              duration: 0.4, 
              ease: [0.4, 0, 0.2, 1] 
            }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative w-full max-w-4xl">
              {/* Header do Menu */}
              <div className="flex items-center justify-between mb-8">
                <motion.h2 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-3xl font-bold text-white bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent"
                >
                  Menu de Navegação
                </motion.h2>
                
                <motion.button
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="p-3 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm transition-all duration-300"
                >
                  <X size={24} />
                </motion.button>
              </div>

              {/* Carrossel */}
              <div className="relative">
                {/* Botão Anterior */}
                <motion.button
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handlePrev}
                  className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 p-3 rounded-full bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm transition-all duration-300 shadow-lg"
                >
                  <ChevronLeft size={24} />
                </motion.button>

                {/* Botão Próximo */}
                <motion.button
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleNext}
                  className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 p-3 rounded-full bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm transition-all duration-300 shadow-lg"
                >
                  <ChevronRight size={24} />
                </motion.button>

                {/* Container do Carrossel */}
                <div
                  ref={carouselRef}
                  className="relative overflow-hidden rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl"
                  onTouchStart={handleTouchStart}
                  onTouchMove={handleTouchMove}
                  onTouchEnd={handleTouchEnd}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={() => setIsDragging(false)}
                >
                  <div className="p-8">
                    {/* Item Atual */}
                    <motion.div
                      key={currentIndex}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="text-center"
                    >
                      {/* Ícone */}
                      <motion.div
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        className="text-8xl mb-6 filter drop-shadow-lg"
                      >
                        {menuItems[currentIndex].icon}
                      </motion.div>

                      {/* Nome */}
                      <h3 className="text-4xl font-bold text-white mb-4">
                        {menuItems[currentIndex].name}
                      </h3>

                      {/* Descrição */}
                      <p className="text-xl text-white/80 mb-8 max-w-md mx-auto">
                        {menuItems[currentIndex].description}
                      </p>

                      {/* Botão de Acesso */}
                      <motion.button
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleItemClick(menuItems[currentIndex])}
                        className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform"
                      >
                        Acessar {menuItems[currentIndex].name}
                      </motion.button>
                    </motion.div>

                    {/* Indicadores */}
                    <div className="flex justify-center items-center gap-3 mt-8">
                      {menuItems.map((_, index) => (
                        <motion.button
                          key={index}
                          whileHover={{ scale: 1.2 }}
                          whileTap={{ scale: 0.8 }}
                          onClick={() => setCurrentIndex(index)}
                          className={`w-3 h-3 rounded-full transition-all duration-300 ${
                            index === currentIndex
                              ? 'bg-white scale-125'
                              : 'bg-white/40 hover:bg-white/60'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Navegação por Teclado */}
                <div className="text-center mt-6 text-white/60 text-sm">
                  Use as setas ← → para navegar ou clique nos indicadores
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default CarouselMenu;
