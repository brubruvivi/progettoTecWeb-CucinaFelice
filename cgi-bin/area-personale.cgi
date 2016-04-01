#!/usr/bin/perl -W
#area-personale.cgi
use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;
use CGI::Session;
use XML::LibXML;
use Fcntl qw(:flock :DEFAULT);

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#inizializzazione variabili di controllo e delle strutture usate nello script
my $indirizzo='area-personale.cgi';
my $indirizzoxmlutenti='../data/utenti.xml';
my $indirizzoxmlcommenti='../data/commenti.xml';
my $session; my $user; my %array; my $admin;
my $stringaget; my %get;
my $stringapost; my %operazione; my %errmodifica; my $nodorimosso;
my $nodoutente; my %utente; my $nodoinfoaggiuntive;
my $fatto;

#controllo parametri metodo get
$stringaget=$ENV{'QUERY_STRING'};
if($stringaget) {
  my @pairs=split(/&/, $stringaget);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/,$pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $get{$name}=$value;
  }
}
#controllo sessione e vari
if($get{action} eq 'logout') { %array=funzioni::checkSession('logout'); } #forse serve aggiungere 'exists $get{action}'
else { %array=funzioni::checkSession; }

#l'utente deve essere loggato
unless($array{stato}) {
  funzioni::printHead( {titolo=>'Area Personale'} );
  funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} );
  funzioni::printPathNav( {dove=>'Area Personale'} );
  print '<p>Effettua il <a href="#login">login</a> per accedere all\'area personale</p>';
  funzioni::printFoot( $indirizzo );
  exit;
}

$session=$array{session};  
$user=$session->param('utente');
$admin=$session->param('admin');

#controllo se arrivo qui tramite il pulsante rimuovi commento
if(exists $get{rimuovi}) {
  my $id=$get{rimuovi};
  #rimuovo il commento con id=$id
  $fatto=funzioni::operazioneCommento( {operazione=>'rimuovi',id=>$id,session=>$session} );
}

#controllo se arrivo qui tramite il pulsante togli segnalazione commento
if(exists $get{togli} and $admin eq 'true') {
  my $id=$get{togli};
  #tolgo la segnalazione del commento il commento
  $fatto=funzioni::operazioneCommento( {operazione=>'togli',id=>$id,admin=>'true'} );
}

#controllo parametri metodo post
read(STDIN,$stringapost,$ENV{'CONTENT_LENGTH'});
if($stringapost) {
  my @pairs=split(/&/,$stringapost);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/,$pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $operazione{$name}=$value;
  }
  unless($operazione{password}) { delete $operazione{password}; }
  unless($operazione{password2}) { delete $operazione{password2}; }
  unless($operazione{email}) { delete $operazione{email}; }
  unless($operazione{nome}) { delete $operazione{nome}; }
  unless($operazione{cognome}) { delete $operazione{cognome}; }
  unless($operazione{abilita}) { delete $operazione{abilita}; }
  unless($operazione{sesso}) { delete $operazione{sesso}; }
  
  if($operazione{action}='modifica') {
    open(*UTENTI,"+< $indirizzoxmlutenti");
    flock(*UTENTI,2);
    my $xmlutenti=XML::LibXML->new()->parse_file($indirizzoxmlutenti);
    my $radice=$xmlutenti->getDocumentElement;
    $nodoutente=$radice->findnodes("//utente[username=\'$user\']")->get_node(1);
    #password
    if(exists $operazione{password} and $operazione{password}=~/[a-zA-Z0-9]{8,20}/ and $operazione{password} eq $operazione{password2}) { #modifico email
      $nodoutente->findnodes('password/text()')->get_node(1)->setData($operazione{password});
      $fatto=1;
    } else {
      unless(exists $operazione{password} and exists $operazione{password2} and $operazione{password} eq $operazione{password2}) { $errmodifica{password}=1; }
    }
    #email
    if(exists $operazione{email} and $operazione{email}=~/[a-zA-Z0-9_.+-]+\@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9_.+-]+/) { #modifico email
      $nodoutente->findnodes('email/text()')->get_node(1)->setData($operazione{email});
      $fatto=1;
    } else { $errmodifica{email}=1; }
    #infoaggiuntive
    $nodoinfoaggiuntive=$nodoutente->findnodes('infoaggiuntive')->get_node(1);
    #campi opzionali
    #nome
    if($operazione{Rnome} and $nodoinfoaggiuntive->exists('nome')) {#rimuovo il nome
      $nodorimosso=$nodoinfoaggiuntive->removeChild($nodoinfoaggiuntive->findnodes('nome')->get_node(1));
    }
    elsif(exists $operazione{nome} and $operazione{nome}=~/\w+( \w+)*/) { #modifico il nome
      if($nodoinfoaggiuntive->exists('nome')) {
	unless($operazione{nome} eq $nodoinfoaggiuntive->findvalue('nome')) {
	  $nodoinfoaggiuntive->findnodes('nome/text()')->get_node(1)->setData($operazione{nome});
	  $fatto=1;
	}
      } else {
	my $nodo=XML::LibXML::Element->new('nome');
	$nodo->appendTextNode($operazione{nome});
	if($nodoinfoaggiuntive->exists('cognome')) { $nodoinfoaggiuntive->insertBefore($nodo,$nodoinfoaggiuntive->findnodes('cognome')->get_node(1)); }
	elsif($nodoinfoaggiuntive->exists('abilita')) { $nodoinfoaggiuntive->insertBefore($nodo,$nodoinfoaggiuntive->findnodes('abilita')->get_node(1)); }
	else { $nodoinfoaggiuntive->appendChild($nodo); }
	$fatto=1;
      }
    }
    #cognome
    if($operazione{Rcognome} and $nodoinfoaggiuntive->exists('cognome')) {#rimuovo il cognome
      $nodorimosso=$nodoinfoaggiuntive->removeChild($nodoinfoaggiuntive->findnodes('cognome')->get_node(1));
    }
    elsif(exists $operazione{cognome} and $operazione{cognome}=~/\w+( \w+)*/) { #modifico il cognome
      if($nodoinfoaggiuntive->exists('cognome')) {
	unless($operazione{cognome} eq $nodoinfoaggiuntive->findvalue('cognome')) {
	  $nodoinfoaggiuntive->findnodes('cognome/text()')->get_node(1)->setData($operazione{cognome});
	  $fatto=1;
	}
      } else {
	my $nodo=XML::LibXML::Element->new('cognome');
	$nodo->appendTextNode($operazione{cognome});
	if($nodoinfoaggiuntive->exists('nome')) { $nodoinfoaggiuntive->insertAfter($nodo,$nodoinfoaggiuntive->findnodes('nome')->get_node(1)); }
	elsif($nodoinfoaggiuntive->exists('abilita')) { $nodoinfoaggiuntive->insertBefore($nodo,$nodoinfoaggiuntive->findnodes('abilita')->get_node(1)); }
	else { $nodoinfoaggiuntive->appendChild($nodo); }
	$fatto=1;
      }
    }
    #abilità
    if($operazione{Rabilita} and $nodoinfoaggiuntive->exists('abilita')) {#rimuovo il abilita
      $nodorimosso=$nodoinfoaggiuntive->removeChild($nodoinfoaggiuntive->findnodes('abilita')->get_node(1));
    }
    elsif(exists $operazione{abilita} and $operazione{abilita}=~/principiante|capace|professionista/) { #modifico il abilita
      if($nodoinfoaggiuntive->exists('abilita')) {
	unless($operazione{abilita} eq $nodoinfoaggiuntive->findvalue('abilita')) {
	  $nodoinfoaggiuntive->findnodes('abilita/text()')->get_node(1)->setData($operazione{abilita});
	  $fatto=1;
	}
      } else {
	my $nodo=XML::LibXML::Element->new('abilita');
	$nodo->appendTextNode($operazione{abilita});
	if($nodoinfoaggiuntive->exists('cognome')) { $nodoinfoaggiuntive->insertAfter($nodo,$nodoinfoaggiuntive->findnodes('cognome')->get_node(1)); }
	elsif($nodoinfoaggiuntive->exists('nome')) { $nodoinfoaggiuntive->insertAfter($nodo,$nodoinfoaggiuntive->findnodes('nome')->get_node(1)); }
	else { $nodoinfoaggiuntive->appendChild($nodo); }
	$fatto=1;
      }
    }
    #sesso
    if($operazione{Rsesso} and $nodoinfoaggiuntive->hasAttribute('sesso')) {#rimuovo il sesso
      $nodorimosso=$nodoinfoaggiuntive->removeAttribute('sesso');
      $fatto=1;
    }
    elsif(exists $operazione{sesso} and $operazione{sesso}=~/M|F/) { #modifico il sesso
      if($nodoinfoaggiuntive->hasAttribute('sesso')) {
	unless($operazione{sesso} eq $nodoinfoaggiuntive->getAttribute('sesso')) { $nodoinfoaggiuntive->setAttribute('sesso',$operazione{sesso}); }
      }else { $nodoinfoaggiuntive->setAttribute('sesso',$operazione{sesso}); }
      $fatto=1;
    }
    if($fatto) { $xmlutenti->toFile($indirizzoxmlutenti); }
    close(*UTENTI);
  }
}

#stampo la pagina html
funzioni::printHead( {titolo=>'Area Personale'} );
funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo,area=>'personale'} );
funzioni::printPathNav( {dove=>'Area Personale'} );

#stampo il contenuto del body
unless($nodoutente) {
#devo caricare xml
  open(*UTENTI,$indirizzoxmlutenti);
  flock(*UTENTI,1);
  my $xmlutenti=XML::LibXML->load_xml({IO=>*UTENTI});
  close(*UTENTI);
  my $radiceu=$xmlutenti->getDocumentElement;
  $nodoutente=$radiceu->findnodes("//utente[username='$user']")->get_node(1);
}
#password rimane vuota
$utente{email}=$nodoutente->findvalue('email');
$utente{infoaggiuntive}=$nodoutente->findnodes('infoaggiuntive')->get_node(1);
if($utente{infoaggiuntive}->exists('nome')) { $utente{nome}=$utente{infoaggiuntive}->findvalue('nome'); }
if($utente{infoaggiuntive}->exists('cognome')) { $utente{cognome}=$utente{infoaggiuntive}->findvalue('cognome'); }
if($utente{infoaggiuntive}->exists('abilita')) { $utente{abilita}=$utente{infoaggiuntive}->findvalue('abilita'); }
if($utente{infoaggiuntive}->hasAttribute('sesso')) { $utente{sesso}=$utente{infoaggiuntive}->getAttribute('sesso'); }

if($admin eq 'true' and $get{action} ne 'modifica') {
#se sei admin in area-personale hai la lista dei commenti segnalati ed un tasto per accedere alle modifiche dei dati personali
  print '<p><a href="'.$indirizzo.'?action=modifica">Link alle informazioni personali</a></p>';
  print '<div><h1>lista dei commenti segnalati da controllare</h1>';
  if($fatto) { print "<h2>$fatto</h2>"; }
  open(*COMMENTI,$indirizzoxmlcommenti);
  flock(*COMMENTI,1);
  my $xmlcommenti=XML::LibXML->load_xml({IO=>*COMMENTI});
  close(*COMMENTI);
  my $radicec=$xmlcommenti->getDocumentElement;
  my @segnalati=$radicec->findnodes("//commento[\@segnalato='si']");
  while(scalar @segnalati) {
    my $nodocommento=shift @segnalati;
    funzioni::printCommento( {nodo=>$nodocommento,indirizzo=>$indirizzo,admin=>'true'} );
  }
  print '</div>';
}
else {
#form di modifica dei valori
  if (exists $errmodifica{stato}) { print '<p>errori mal controllati dal javascript</p>'; } #forse non serve tutto il controllo errori
  if($admin eq 'true') { print '<p><a href="'.$indirizzo.'">link alla lista dei commenti segnalati</a></p>'; }
  if($fatto) { print '<h2>hai modificato il tuo profilo con successo,</h2>'; }
  print '<h1>Qui puoi modificare i dati personali</h1><h2>I campi obbligatori sono contrassegnati da un asterisco (*)</h2><h3>L\'username può contenere lettere maiuscole minuscole e numeri, la password deve avere almeno 8 caratteri tra lettere maiuscole o minuscole e numeri.</h3>';
  print '<form method="post" id="modifica" onsubmit="return controllatuz()" action="';
  if($admin eq 'true' and $get{action} eq 'modifica'){ print 'area-personale.cgi?action=modifica'; }
  else { print 'area-personale.cgi'; }
  print <<EOF1;
"><p><label class="left" for="password1">Nuova password*</label>
<input class="middle" type="password" name="password" onblur="controllapass()" id="password1">
<span class="right" id="checkpass"></span></p>
<p><label class="left" for="password2">Conferma nuova password*</label>
<input class="middle" type="password" name="password2" onblur="controllapsw2()" id="password2"/>
<span class="right" id="checkconf"></span></p>
<p><label class="left" for="email">E-mail*</label>
<input class="middle" type="text" name="email" id="email" onblur="controllamail()" value="$utente{email}"/>
<span class="right" id="checkmail"></span></p>
<p><label class="left" for="nome">Nome</label>
<input class="middle" type="text" name="nome" id="nome" value="$utente{nome}"/>
<span class="right"><label for="Rnome">rimuovi nome</label><input type="checkbox" name="Rnome" id="Rnome" value="1"></span></p>
<p><label class="left" for="cognome">Cognome</label>
<input class="middle" type="text" name="cognome" id="cognome" value="$utente{cognome}"/>
<span class="right"><label for="Rcognome">rimuovi cognome</label><input type="checkbox" name="Rcognome" id="Rcognome" value="1"></span></p>
EOF1

  print '<p><label class="left" for="abilita">Abilità</label><span class="right"><label for="principiante">Principiante</label>';
  print '<input type="radio" name="abilita" id="principiante" value="principiante"';
  if($utente{abilita} eq 'principiante') { print ' checked="checked"';  }
  print '/><label class="justify" for="intermedia">Intermedia</label><input type="radio" name="abilita" id="intermedia" value="intermedia"';
  if($utente{abilita} eq 'intermedia') { print ' checked="checked"';  }
  print '/><label class="justify" for="professionista">Professionista</label><input type="radio" name="abilita" id="professionista" value="professionista"';
  if($utente{abilita} eq 'professionista') { print ' checked="checked"';  }
  print '/><label class="justify" for="Rabilita">Rimuovi abilita</label><input type="checkbox" name="Rabilita" id="Rabilita" value="1"></span></p>';
  print '<p><label class="left" for="sesso">Sesso</label><span class="right"><label for="male">Maschile </label><input type="radio" name="sesso" id="male" value="M"';
  if($utente{sesso} eq 'M') { print ' checked="checked"';  }
  print '/><label class="justify" for="female">Femminile </label><input type="radio" name="sesso" id="female" value="F"';
  if($utente{sesso} eq 'F') { print ' checked="checked"';  }
  print '/><label class="justify" for="Rsesso">Rimuovi sesso</label><input type="checkbox" name="Rsesso" id="Rsesso" value="1"></span></p>';
  print '<p><input class="button" type="submit" name="action" value="modifica"/></p></form>';
  funzioni::printAncora;
}
funzioni::printFoot( $indirizzo );

#fine