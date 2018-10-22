##  merge_results.pl
##  June 6, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
##  program to merge classifier output with texts
##
##  execute in unix: perl merge_results.pl 0 svm_ntf2011.predict svm_ntf2011.dat
##  The first argument corresponds to the cutoff, >=cutoff documents are sorted as positive, <cutoff documents are sorted as negative
##
##  Output: sorted_pos.txt sorted_pos.tsv sorted_neg.txt sorted_pos.tsv
##
##  Script requires the "documents.txt" file and "MID.ISO.CODES.txt" to be in the same directory as merge_results.pl
##
##  Programming for origin files supported by National Science Foundation Political Science Program Grant
##  SES-1528624 "Collaborative Research: Updating the Militarized Dispute Data Through Crowdsourcing: MID5"
##
##  PROGRAM ORIGIN:
##  Adapted from the MID 4.0 Data Collection project
##
##  Programming for origin files supported by National Science Foundation Political Science Program Grant
##  SES-0719634 "Improving the Efficiency of Militarized Interstate Dispute Data Collection using
##  Automated Textual Analysis" and SES-0924240, "MID4: Updating the Militarized Dispute Data Set
##  2002-2010."
##
##   Redistribution and use in source and binary forms, with or without modification,
##   are permitted under the terms of the GNU General Public License:
##   http://www.opensource.org/licenses/gpl-license.html
##


#!/usr/local/bin/perl
use strict;
use warnings;

sub TrimString {
    $_[0] =~ s/^\s+//; #remove leading whites
    $_[0] =~ s/\s+$//; #remove trailing spaces
    $_[0] =~ s/\t/\ /; #remove tabs in string
    $_[0] =~ s/\r/\ /; #remove carriage return in string
    $_[0] =~ s/\n/\ /; #remove newline in string
    return $_[0];
}


my $sortVal = $ARGV[0];
my $predict = $ARGV[1];
my $featureData = $ARGV[2];
my $code_file   = "MID.ISO.CODES.txt";
my $documents_file = "documents2015factiva3.txt";
my %posHash = ();
my %negHash = ();

if (@ARGV != 3 && -t STDIN && -t STDERR) {
    print STDERR "$0: merge_results.pl requires three inputs: sort value; predictions files; features file. Exiting.\n";
    exit;
}

## checking if files exist
die "The file $code_file does not exist, and I can't go on without it." unless -e $code_file;
die "The file documents.txt does not exist, and I can't go on without it." unless -e $documents_file;
die "The file $predict does not exist. This input is the predict file." unless -e $predict;
die "The file $featureData does not exist. This input is the features file." unless -e $featureData;

# read COW codes

open(DAT, $code_file) || die("Could not open code conversion  file $code_file");
chomp(my @field = <DAT>);
my @codes;
my $i = 0;

foreach (@field) {
    my @datline = split("\t", $_);
    $codes[$i][0] = $datline[2];
    $codes[$i][1] = $datline[1];
    ++$i;
}

open(FPRED,$predict)  or die "Can\'t open predictions file; error $!";
open(FDAT,$featureData)  or die "Can\'t open features file; error $!";


open(FPOSa,">sorted_pos.txt") or die "Can\'t open output file ; error $!";
open(FNEGa,">sorted_neg.txt") or die "Can\'t open output file ; error $!";

# vjd 8/23: file which contains the features vectors for all positives
open(POSFEATS,">sorted_pos.dat") or die "Can\'t open output file ; error $!";

my $ncase = 0;
my $npos  = 0;
my $nneg  = 0;

while (my $line = <FDAT>) {
    $line =~ s/\R//g;
  chomp(my $pred = <FPRED>);
  my $id = substr($line,index($line,"#"));
    $id = substr($id, 2,);
  ++$ncase;
  if ($pred >= $sortVal) {
    $posHash{$id} = $pred;
      # print FPOSb $pred,"\t",$id,"\n";
    print POSFEATS $line;
    ++$npos;
  }
  else  {
    $negHash{$id} = $pred;
      # print FNEGb $pred,"\t",$id,"\n";
    ++$nneg;
  }
}

print "Positive cases: ",$npos,"  Total cases: ", $ncase,"  Proportion: ",($npos/$ncase),"\n";
print "Negative cases: ",$nneg,"  Total cases: ", $ncase,"  Proportion: ",($nneg/$ncase),"\n";
print POSFEATS "Positive cases: ",$npos,"  Total cases: ", $ncase,"  Proportion: ",($npos/$ncase),"\n";


close(POSFEATS) or die "Can\'t close output file ; error $!";
open(FIN, $documents_file) or die "Can\'t open documents.txt; error $!";


my $story = "";
my $storyid = "";

while (my $line = <FIN>) {
    
    $story = $story.$line;
    
    if($line =~ m/Key: /) {
        $storyid = &TrimString($line);
        $storyid =~ s/Key: //;
        next;
    }
    
    if($line =~ m/>>>>>>>>>>>>>>>>>>>>>>/) {
        while ($line = <FIN>) {
            if ($line =~ m/--------------------------------/) {
                $story = $story.$line;
                if (exists $posHash{$storyid}) {
                    print FPOSa $story;
                    #print FPOSb "$posHash{$storyid}\t$storyid\t$headline\t$date\t$source\t\n";
                } elsif (exists $negHash{$storyid}) {
                    print FNEGa $story;
                    # print FNEGb "$negHash{$storyid}\t$storyid\t$headline\t$date\t$source\n";
                }
                
                $story = "";
                $storyid = "";

                last;
            }
            $story = $story.$line;
            if (eof(FIN)) { print "Error: Unexpected eof in search for end of story while reading documents.txt\n"; last;}
        }
    }
    
}


close(FPOSa) or die "Can\'t close output file ; error $!";
close(FNEGa) or die "Can\'t close output file ; error $!";
close(FDAT) or die "Can\'t close input file ; error $!";
close(FPRED) or die "Can\'t close input file ; error $!";
close(FIN) or die "Can\'t close documents; error $!";
print "Program has finished!\n";

exit;



